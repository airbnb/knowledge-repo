from ..proxies import current_app
from ..utils.shared import get_blueprint
from flask import (
    current_app,
    redirect,
    render_template,
    url_for,
)
from flask_login import logout_user, login_required
from flask_principal import identity_changed, AnonymousIdentity

blueprint = get_blueprint('auth', __name__)


@blueprint.route('/auth/login', methods=['GET', 'POST'])
def login():

    providers = current_app.auth_providers

    if len(providers) == 1:
        provider_name = providers[0].name
        return redirect(url_for(f'auth_provider_{provider_name}.prompt'))

    return render_template(
        'auth-switcher.html',
        providers=[{
            'name': provider.name,
            'icon_uri': provider.icon_uri,
            'link_text': provider.link_text} for provider in providers]
    )


@blueprint.route("/auth/logout")
@login_required
def logout():
    logout_user()

    # Notify flask principal that the user has logged out
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('index.render_feed'))
