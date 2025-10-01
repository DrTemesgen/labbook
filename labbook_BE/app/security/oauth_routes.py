# app/security/oauth_routes.py
import time
import base64

from urllib.parse import urlparse
from flask import Blueprint, request, redirect, jsonify, session

# Authlib
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from authlib.oauth2.rfc6750 import BearerTokenValidator
from authlib.integrations.flask_oauth2 import ResourceProtector

from app.models.DB import DB


bp_oauth = Blueprint('oauth', __name__)


def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


def _load_client(client_id: str):
    cur = DB.cursor()
    cur.execute(
        "SELECT * FROM oauth2_client WHERE oacl_client_id=%s AND oacl_is_active='Y'",
        (client_id,)
    )
    return cur.fetchone()


def _validate_redirect_uri(client_row: dict, redirect_uri: str) -> bool:
    # DB stores only PATH (e.g. "/oauth/callback")
    raw = (client_row.get('oacl_redirect_uris') or '').replace('\r', '\n')
    paths = [p.strip() for p in raw.split('\n') if p.strip()]
    if not paths:
        return False
    u = urlparse(redirect_uri)
    if u.scheme not in ('https', 'http'):
        return False
    if u.scheme == 'http' and u.hostname not in ('localhost', '127.0.0.1') \
       and not (u.hostname or '').startswith(('10.', '192.168.')):
        return False
    return u.path in paths


# --------- Authlib glue ---------

def query_client(client_id):
    row = _load_client(client_id)
    if not row:
        return None

    class Client:
        client_id = row['oacl_client_id']
        client_name = row['oacl_client_name']
        token_endpoint_auth_method = row['oacl_token_endpoint_auth_method']
        grant_types = (row['oacl_grant_types'] or '').split()
        response_types = (row.get('oacl_response_types') or 'code').split()
        scope = row['oacl_scope']
        redirect_uris = [p.strip() for p in (row['oacl_redirect_uris'] or '').replace('\r', '\n').split('\n') if p.strip()]
        client_secret = row['oacl_client_secret'] or None

        def check_redirect_uri(self, redirect_uri):
            # path-only policy
            return _validate_redirect_uri(row, redirect_uri)

    return Client()


def save_token(token, req):
    cur = DB.cursor(ecr=True)
    cur.execute("""
        INSERT INTO oauth2_token
        (oato_client_id, oato_token_type, oato_access_token, oato_refresh_token,
         oato_scope, oato_revoked, oato_issued_at, oato_expires_in)
        VALUES (%s,%s,%s,%s,%s,'N',%s,%s)
    """, (
        req.client.client_id,
        token.get('token_type', 'Bearer'),
        token['access_token'],
        token.get('refresh_token'),
        token.get('scope', ''),
        int(time.time()),
        int(token.get('expires_in') or 3600)
    ))


class AuthorizationCodeGrantPKCE(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, req):
        cur = DB.cursor(ecr=True)
        cur.execute("""
            INSERT INTO oauth2_code
            (oaco_code, oaco_client_id, oaco_redirect_uri, oaco_scope, oaco_auth_time,
             oaco_nonce, oaco_code_challenge, oaco_code_challenge_method, oaco_expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            code,
            req.client.client_id,
            req.redirect_uri or '',
            req.scope or '',
            int(time.time()),
            req.data.get('nonce', ''),
            req.data.get('code_challenge', ''),
            req.data.get('code_challenge_method', ''),
            int(time.time()) + 600
        ))
        return code

    def query_authorization_code(self, code, client):
        cur = DB.cursor()
        cur.execute("SELECT * FROM oauth2_code WHERE oaco_code=%s AND oaco_client_id=%s", (code, client.client_id))
        return cur.fetchone()

    def delete_authorization_code(self, code):
        cur = DB.cursor(ecr=True)
        cur.execute("DELETE FROM oauth2_code WHERE oaco_code=%s", (code['oaco_code'],))

    def authenticate_user(self, code):
        # Attach your logged-in user (session)
        class U:
            pass
        u = U()
        u.id = session.get('user_id', 0)
        return u

    def validate_code_challenge(self, code_verifier, authorization_code):
        method = authorization_code['oaco_code_challenge_method']
        challenge = authorization_code['oaco_code_challenge']
        return CodeChallenge(method).verify(code_verifier, challenge)


# Create server bound to this blueprint's app on first request
authorization = AuthorizationServer(
    query_client=query_client,
    save_token=save_token
)
authorization.register_grant(AuthorizationCodeGrantPKCE, [CodeChallenge(required=True)])

# ----- Resource ----
require_oauth = ResourceProtector()


class MyBearerTokenValidator(BearerTokenValidator):
    # Check if the token exists and is not expired
    def authenticate_token(self, token_string):
        cur = DB.cursor()
        cur.execute("""
            SELECT * FROM oauth2_token
            WHERE oato_access_token=%s AND oato_revoked='N'
            LIMIT 1
        """, (token_string,))
        tok = cur.fetchone()
        if not tok:
            return None
        now = int(time.time())
        if now > (tok['oato_issued_at'] + tok['oato_expires_in']):
            return None
        return tok

    # Return True if the HTTP request itself is invalid
    def request_invalid(self, request):
        return False

    # Return True if the token is marked as revoked
    def token_revoked(self, token):
        return token.get('oato_revoked') == 'Y'

    # Return True if required scopes are missing
    def scope_insufficient(self, token, scope):
        if not scope:
            return False
        token_scopes = (token.get('oato_scope') or '').split()
        needed = scope.split()
        return not all(s in token_scopes for s in needed)


# Register the validator
require_oauth.register_token_validator(MyBearerTokenValidator())


# --------- Routes ---------

@bp_oauth.route('/oauth/authorize', methods=['GET', 'POST'])
def oauth_authorize():
    if 'user_id' not in session:
        session['next'] = request.url
        return redirect('/')
    # Authlib handles response building (validations, state, etc.)
    return authorization.create_authorization_response(grant_user=type('U', (), {'id': session['user_id']}))


@bp_oauth.route('/oauth/token', methods=['POST'])
def oauth_token():
    return authorization.create_token_response()


@bp_oauth.route('/confirm-access', methods=['POST'])
def confirm_access():
    args = request.get_json() or {}
    id_user = args.get('id_user', None)
    if id_user is None:
        return jsonify({'error': 'id_user missing'}), 400

    # Set BE session (used by /services/oauth/authorize)
    session['user_id'] = int(id_user)
    session.modified = True

    # Only return the paused OAuth authorize URL if presetn; no fallback here
    redirect_url = session.pop('next', None)
    return jsonify({'redirect_url': redirect_url})
