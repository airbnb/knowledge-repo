import json
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_user
from six.moves.urllib.parse import urljoin

from ..models import User
from ..proxies import db_session
from ..utils.auth import is_safe_url

from ..auth_provider import KnowledgeAuthProvider


PRESETS = {
    'bitbucket': {
        'base_url': 'https://api.bitbucket.org/2.0/',
        'authorization_url': 'https://bitbucket.org/site/oauth2/authorize',
        'token_url': 'https://bitbucket.org/site/oauth2/access_token',
        'auto_refresh_url': 'https://bitbucket.org/site/oauth2/access_token',
        'scopes': 'account',
        'user_info_endpoint': 'user',
        'user_info_mapping': {
            'identifier': 'username',
            'name': 'display_name',
            'photo_uri': ['links', 'avatar']
        }
    },
    'github': {
        'base_url': 'https://api.github.com/',
        'authorization_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'auto_refresh_url': None,
        'scopes': None,
        'user_info_endpoint': 'user',
        'user_info_mapping': {
            'identifier': 'email',
            'name': 'name',
            'photo_uri': 'avatar_url'
        }
    },
    'google': {
        'base_url': 'https://www.googleapis.com/oauth2/v2/',
        'authorization_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'auto_refresh_url': 'https://accounts.google.com/o/oauth2/token',
        'scopes': [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ],
        'user_info_endpoint': 'userinfo',
        'user_info_mapping': {
            'identifier': 'email',
            'name': 'name',
            'photo_uri': 'picture'
        }
    }
}


def _resolve_oauth_config(name, local_namespace, config, *variables):
    presets = PRESETS.get(name, {})
    output = []
    for variable in variables:
        value = local_namespace.get(variable, None)
        if value is None:
            value = config.get('OAUTH_{}_{}'.format(name, variable).upper(), None)
        if value is None:
            value = presets.get(variable, None)
        output.append(value)
    return output


class OAuth2Provider(KnowledgeAuthProvider):
    _registry_keys = list(PRESETS.keys())

    def init(self,
             authorization_url=None,
             token_url=None,
             auto_refresh_url=None,
             scopes=None,
             user_info_endpoint=None,
             client_id=None,
             client_secret=None,
             user_info_mapping=None,
             validate=None):

        (self.base_url,
         self.authorization_url,
         self.token_url,
         self.auto_refresh_url,
         self.scopes,
         self.user_info_endpoint,
         self.client_id,
         self.client_secret,
         self.user_info_mapping,
         validate) = _resolve_oauth_config(
            self.name,
            locals(),
            self.app.config,
            'base_url',
            'authorization_url',
            'token_url',
            'auto_refresh_url',
            'scopes',
            'user_info_endpoint',
            'client_id',
            'client_secret',
            'user_info_mapping',
            'validate'
        )
        if validate is not None:
            self.validate = lambda x: validate(self, x)

        redirect_url = self.app.config['SERVER_NAME'] or 'localhost:7000'
        if self.app.config['APPLICATION_ROOT']:
            redirect_url = '/'.join((redirect_url, self.app.config['APPLICATION_ROOT']))

        # Import OAuth deps here so we do not have a hard dependency on them
        from requests_oauthlib import OAuth2Session
        self.oauth_client = OAuth2Session(
            client_id=self.client_id,
            scope=self.scopes,
            redirect_uri='http://{}/auth/login/{}/authorize'.format(redirect_url, self.name),
            auto_refresh_url=self.auto_refresh_url
        )

    def prompt(self):
        return redirect(self.oauth_client.authorization_url(self.authorization_url)[0])

    def get_endpoint_url(self, endpoint):
        return urljoin(self.base_url, endpoint)

    def get_user(self):
        code = request.args.get('code')
        state = request.args.get('state')

        self.oauth_client.state = state
        self.oauth_client.fetch_token(self.token_url, client_secret=self.client_secret, code=code)

        return self.extract_user_from_api()

    def extract_user_from_api(self):

        def extract_from_dict(d, key):
            if isinstance(key, (list, tuple)):
                if len(key) == 1:
                    key = key[0]
                else:
                    return extract_from_dict(d[key[0]], key[1:])
            if isinstance(key, str):
                return d[key]
            raise RuntimeError("Invalid key type: {}.".format(key))

        response = self.oauth_client.get(self.get_endpoint_url(self.user_info_endpoint))
        try:
            r = json.loads(response.content)

            user = User(identifier=extract_from_dict(r, self.user_info_mapping['identifier']))
            if 'name' in self.user_info_mapping:
                user.name = extract_from_dict(r, self.user_info_mapping['name'])
            if 'photo_uri' in self.user_info_mapping:
                user.photo_uri = extract_from_dict(r, self.user_info_mapping['photo_uri'])
        except:
            raise RuntimeError("Failure to extract user information from:\n\n {}".format(response.content))

        return user
