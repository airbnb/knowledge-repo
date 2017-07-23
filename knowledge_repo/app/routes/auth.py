from flask import flash, redirect, render_template, request, current_app, Blueprint, url_for
from flask_login import login_user, logout_user, login_required
from flask_principal import identity_changed, AnonymousIdentity, PermissionDenied

from ..models import User
from ..proxies import current_app
from ..utils.auth import is_safe_url

blueprint = Blueprint('auth', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/auth/login', methods=['GET', 'POST'])
def login():

    providers = current_app.auth_providers

    if len(providers) == 1:
        return redirect(url_for('auth_provider.{}.prompt'.format(providers[0].name)))

    return render_template(
        'auth-switcher.html',
        providers=[{'name': provider.name, 'icon_uri': provider.icon_uri, 'link_text': provider.link_text} for provider in providers]
    )

# @blueprint.route('/auth/login/<provider>', methods=['GET', 'POST'])
# def provider_login(provider):
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     if request.method == 'POST':
#         user = request.form['username']
#         login_user(User(identifier=user))
#
#         flash('Logged in successfully.')
#
#         next = request.args.get('next')
#         # is_safe_url should check if the url is safe for redirects.
#         # See http://flask.pocoo.org/snippets/62/ for an example.
#         if not is_safe_url(next):
#             return flask.abort(400)
#
#         return redirect(next or url_for('index.render_feed'))
#     return render_template('login.html')


@blueprint.route("/auth/logout")
@login_required
def logout():
    logout_user()

    # Notify flask principal that the user has logged out
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('index.render_feed'))
