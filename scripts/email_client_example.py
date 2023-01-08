# app.py
#
# To run this example, please get the MAIL_PASSWORD (i.e., API_KEY)
# following the instructions given by SendGrid at here:
#   https://sendgrid.com/blog/sending-emails-from-python-flask-applications-with-twilio-sendgrid/,
# then run the following commands in a terminal:
#
# $ python3 -m venv venv
# $ source venv/bin/activate
# (venv) $ pip install flask flask-mail
# (venv) $ python3 app.py


from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["SECRET_KEY"] = "top-secret!"
app.config["MAIL_SERVER"] = "smtp.sendgrid.net"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "apikey"
app.config["MAIL_PASSWORD"] = "<Get it from SendGrid>"
app.config["MAIL_DEFAULT_SENDER"] = "<Test sender email>"


with app.app_context():
    mail = Mail(app)
    msg = Message("Twilio SendGrid Test Email", recipients=["<Test recipient email>"])
    msg.body = "This is a test email!"
    msg.html = "<p>This is a test email!</p>"
    mail.send(msg)
