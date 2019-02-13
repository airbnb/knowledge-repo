# -*- coding: utf-8 -*-
"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement

__version__ = '0.9.1'

import re
import blinker
import smtplib
import sys
import time
import unicodedata

from email import charset
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate, formataddr, make_msgid, parseaddr
from contextlib import contextmanager

from flask import current_app

PY3 = sys.version_info[0] == 3

PY34 = PY3 and sys.version_info[1] >= 4

if PY3:
    string_types = str,
    text_type = str
    from email import policy
    message_policy = policy.SMTP
else:
    string_types = basestring,
    text_type = unicode
    message_policy = None

charset.add_charset('utf-8', charset.SHORTEST, None, 'utf-8')


class FlaskMailUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj, *args):
        self.obj = obj
        UnicodeDecodeError.__init__(self, *args)

    def __str__(self):
        original = UnicodeDecodeError.__str__(self)
        return '%s. You passed in %r (%s)' % (original, self.obj, type(self.obj))


def force_text(s, encoding='utf-8', errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, text_type):
        return s

    try:
        if not isinstance(s, string_types):
            if PY3:
                if isinstance(s, bytes):
                    s = text_type(s, encoding, errors)
                else:
                    s = text_type(s)
            elif hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                s = text_type(bytes(s), encoding, errors)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise FlaskMailUnicodeDecodeError(s, *e.args)
        else:
            s = ' '.join([force_text(arg, encoding, strings_only,
                    errors) for arg in s])
    return s

def sanitize_subject(subject, encoding='utf-8'):
    try:
        subject.encode('ascii')
    except UnicodeEncodeError:
        try:
            subject = Header(subject, encoding).encode()
        except UnicodeEncodeError:
            subject = Header(subject, 'utf-8').encode()
    return subject

def sanitize_address(addr, encoding='utf-8'):
    if isinstance(addr, string_types):
        addr = parseaddr(force_text(addr))
    nm, addr = addr

    try:
        nm = Header(nm, encoding).encode()
    except UnicodeEncodeError:
        nm = Header(nm, 'utf-8').encode()
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if '@' in addr:
            localpart, domain = addr.split('@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna').decode('ascii')
            addr = '@'.join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return formataddr((nm, addr))


def sanitize_addresses(addresses, encoding='utf-8'):
    return map(lambda e: sanitize_address(e, encoding), addresses)


def _has_newline(line):
    """Used by has_bad_header to check for \\r or \\n"""
    if line and ('\r' in line or '\n' in line):
        return True
    return False

class Connection(object):
    """Handles connection to host."""

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        if self.mail.suppress:
            self.host = None
        else:
            self.host = self.configure_host()

        self.num_emails = 0

        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host:
            self.host.quit()

    def configure_host(self):
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port)

        host.set_debuglevel(int(self.mail.debug))

        if self.mail.use_tls:
            host.starttls()
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)

        return host

    def send(self, message, envelope_from=None):
        """Verifies and sends message.

        :param message: Message instance.
        :param envelope_from: Email address to be used in MAIL FROM command.
        """
        assert message.send_to, "No recipients have been added"

        assert message.sender, (
                "The message does not specify a sender and a default sender "
                "has not been configured")

        if message.has_bad_headers():
            raise BadHeaderError

        if message.date is None:
            message.date = time.time()

        if self.host:
            self.host.sendmail(sanitize_address(envelope_from or message.sender),
                               list(sanitize_addresses(message.send_to)),
                               message.as_bytes() if PY3 else message.as_string(),
                               message.mail_options,
                               message.rcpt_options)

        email_dispatched.send(message, app=current_app._get_current_object())

        self.num_emails += 1

        if self.num_emails == self.mail.max_emails:
            self.num_emails = 0
            if self.host:
                self.host.quit()
                self.host = self.configure_host()

    def send_message(self, *args, **kwargs):
        """Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        self.send(Message(*args, **kwargs))


class BadHeaderError(Exception):
    pass


class Attachment(object):
    """Encapsulates file attachment information.

    :versionadded: 0.3.5

    :param filename: filename of attachment
    :param content_type: file mimetype
    :param data: the raw file data
    :param disposition: content-disposition (if any)
    """

    def __init__(self, filename=None, content_type=None, data=None,
                 disposition=None, headers=None):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition or 'attachment'
        self.headers = headers or {}


class Message(object):
    """Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **MAIL_DEFAULT_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    :param reply_to: reply-to address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message
    :param mail_options: A list of ESMTP options to be used in MAIL FROM command
    :param rcpt_options:  A list of ESMTP options to be used in RCPT commands
    """

    def __init__(self, subject='',
                 recipients=None,
                 body=None,
                 html=None,
                 sender=None,
                 cc=None,
                 bcc=None,
                 attachments=None,
                 reply_to=None,
                 date=None,
                 charset=None,
                 extra_headers=None,
                 mail_options=None,
                 rcpt_options=None):

        sender = sender or current_app.extensions['mail'].default_sender

        if isinstance(sender, tuple):
            sender = "%s <%s>" % sender

        self.recipients = recipients or []
        self.subject = subject
        self.sender = sender
        self.reply_to = reply_to
        self.cc = cc or []
        self.bcc = bcc or []
        self.body = body
        self.html = html
        self.date = date
        self.msgId = make_msgid()
        self.charset = charset
        self.extra_headers = extra_headers
        self.mail_options = mail_options or []
        self.rcpt_options = rcpt_options or []
        self.attachments = attachments or []

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    def _mimetext(self, text, subtype='plain'):
        """Creates a MIMEText object with the given subtype (default: 'plain')
        If the text is unicode, the utf-8 charset is used.
        """
        charset = self.charset or 'utf-8'
        return MIMEText(text, _subtype=subtype, _charset=charset)

    def _message(self):
        """Creates the email"""
        ascii_attachments = current_app.extensions['mail'].ascii_attachments
        encoding = self.charset or 'utf-8'

        attachments = self.attachments or []

        if len(attachments) == 0 and not self.html:
            # No html content and zero attachments means plain text
            msg = self._mimetext(self.body)
        elif len(attachments) > 0 and not self.html:
            # No html and at least one attachment means multipart
            msg = MIMEMultipart()
            msg.attach(self._mimetext(self.body))
        else:
            # Anything else
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(self._mimetext(self.body, 'plain'))
            alternative.attach(self._mimetext(self.html, 'html'))
            msg.attach(alternative)

        if self.subject:
            msg['Subject'] = sanitize_subject(force_text(self.subject), encoding)

        msg['From'] = sanitize_address(self.sender, encoding)
        msg['To'] = ', '.join(list(set(sanitize_addresses(self.recipients, encoding))))

        msg['Date'] = formatdate(self.date, localtime=True)
        # see RFC 5322 section 3.6.4.
        msg['Message-ID'] = self.msgId

        if self.cc:
            msg['Cc'] = ', '.join(list(set(sanitize_addresses(self.cc, encoding))))

        if self.reply_to:
            msg['Reply-To'] = sanitize_address(self.reply_to, encoding)

        if self.extra_headers:
            for k, v in self.extra_headers.items():
                msg[k] = v

        SPACES = re.compile(r'[\s]+', re.UNICODE)
        for attachment in attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)

            filename = attachment.filename
            if filename and ascii_attachments:
                # force filename to ascii
                filename = unicodedata.normalize('NFKD', filename)
                filename = filename.encode('ascii', 'ignore').decode('ascii')
                filename = SPACES.sub(u' ', filename).strip()

            try:
                filename and filename.encode('ascii')
            except UnicodeEncodeError:
                if not PY3:
                    filename = filename.encode('utf8')
                filename = ('UTF8', '', filename)

            f.add_header('Content-Disposition',
                         attachment.disposition,
                         filename=filename)

            for key, value in attachment.headers:
                f.add_header(key, value)

            msg.attach(f)
        if message_policy:
            msg.policy = message_policy

        return msg

    def as_string(self):
        return self._message().as_string()

    def as_bytes(self):
        if PY34:
            return self._message().as_bytes()
        else: # fallback for old Python (3) versions
            return self._message().as_string().encode(self.charset or 'utf-8')

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()

    def has_bad_headers(self):
        """Checks for bad headers i.e. newlines in subject, sender or recipients.
        RFC5322: Allows multiline CRLF with trailing whitespace (FWS) in headers
        """

        headers = [self.sender, self.reply_to] + self.recipients
        for header in headers:
            if _has_newline(header):
                return True

        if self.subject:
            if _has_newline(self.subject):
                for linenum, line in enumerate(self.subject.split('\r\n')):
                    if not line:
                        return True
                    if linenum > 0 and line[0] not in '\t ':
                        return True
                    if _has_newline(line):
                        return True
                    if len(line.strip()) == 0:
                        return True
        return False

    def is_bad_headers(self):
        from warnings import warn
        msg = 'is_bad_headers is deprecated, use the new has_bad_headers method instead.'
        warn(DeprecationWarning(msg), stacklevel=1)
        return self.has_bad_headers()

    def send(self, connection):
        """Verifies and sends the message."""

        connection.send(self)

    def add_recipient(self, recipient):
        """Adds another recipient to the message.

        :param recipient: email address of recipient.
        """

        self.recipients.append(recipient)

    def attach(self,
               filename=None,
               content_type=None,
               data=None,
               disposition=None,
               headers=None):
        """Adds an attachment to the message.

        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        """
        self.attachments.append(
            Attachment(filename, content_type, data, disposition, headers))


class _MailMixin(object):

    @contextmanager
    def record_messages(self):
        """Records all messages. Use in unit tests for example::

            with mail.record_messages() as outbox:
                response = app.test_client.get("/email-sending-view/")
                assert len(outbox) == 1
                assert outbox[0].subject == "testing"

        You must have blinker installed in order to use this feature.
        :versionadded: 0.4
        """

        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message, app):
            outbox.append(message)

        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)

    def send(self, message):
        """Sends a single message instance. If TESTING is True the message will
        not actually be sent.

        :param message: a Message instance.
        """

        with self.connect() as connection:
            message.send(connection)

    def send_message(self, *args, **kwargs):
        """Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        self.send(Message(*args, **kwargs))

    def connect(self):
        """Opens a connection to the mail host."""
        app = getattr(self, "app", None) or current_app
        try:
            return Connection(app.extensions['mail'])
        except KeyError:
            raise RuntimeError("The curent application was not configured with Flask-Mail")


class _Mail(_MailMixin):
    def __init__(self, server, username, password, port, use_tls, use_ssl,
                 default_sender, debug, max_emails, suppress,
                 ascii_attachments=False):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.default_sender = default_sender
        self.debug = debug
        self.max_emails = max_emails
        self.suppress = suppress
        self.ascii_attachments = ascii_attachments


class Mail(_MailMixin):
    """Manages email messaging

    :param app: Flask instance
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.state = self.init_app(app)
        else:
            self.state = None

    def init_mail(self, config, debug=False, testing=False):
        return _Mail(
            config.get('MAIL_SERVER', '127.0.0.1'),
            config.get('MAIL_USERNAME'),
            config.get('MAIL_PASSWORD'),
            config.get('MAIL_PORT', 25),
            config.get('MAIL_USE_TLS', False),
            config.get('MAIL_USE_SSL', False),
            config.get('MAIL_DEFAULT_SENDER'),
            int(config.get('MAIL_DEBUG', debug)),
            config.get('MAIL_MAX_EMAILS'),
            config.get('MAIL_SUPPRESS_SEND', testing),
            config.get('MAIL_ASCII_ATTACHMENTS', False)
        )

    def init_app(self, app):
        """Initializes your mail settings from the application settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        """
        state = self.init_mail(app.config, app.debug, app.testing)

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mail'] = state
        return state

    def __getattr__(self, name):
        return getattr(self.state, name, None)


signals = blinker.Namespace()

email_dispatched = signals.signal("email-dispatched", doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""")
