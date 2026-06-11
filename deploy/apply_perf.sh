#!/bin/bash
set -euo pipefail
R=/opt/labbook
FE="$R/labbook_FE/app"
HT=/home/aslmacademy/labbook.aslmacademy.org/.htaccess
TS=$(date +%s)
echo "=== backup __init__.py + .htaccess ==="
cp "$FE/__init__.py" "$FE/__init__.py.bak.perf.$TS"
cp "$HT" "$HT.bak.$TS"

echo "=== 1/3 add gzip + static caching to __init__.py ==="
python3 - "$FE/__init__.py" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
if 'add_perf_headers' in s:
    print("  already present"); sys.exit(0)

imp_old = "import re\nimport tomllib\n"
imp_new = "import re\nimport tomllib\nimport gzip\nfrom io import BytesIO\n"
assert imp_old in s, "import anchor not found"
s = s.replace(imp_old, imp_new, 1)

anchor = "    session.permanent = True\n    session.modified = True\n\n\nLANG_SELECT = {"
block = '''    session.permanent = True
    session.modified = True


# -----------------------------------------------------------------------------
# Performance: gzip text responses + long-cache static assets
# -----------------------------------------------------------------------------
# Done at the app layer (not Apache/nginx) so it stays fully self-contained to
# LabBook and is passed through unchanged by the reverse proxies in front.
# -----------------------------------------------------------------------------
_COMPRESSIBLE = ('text/html', 'text/css', 'text/xml', 'text/plain',
                 'application/javascript', 'application/x-javascript',
                 'application/json', 'image/svg+xml', 'application/xml')
_STATIC_EXTS = {'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'ico',
                'woff', 'woff2', 'svg', 'ttf', 'eot'}


@app.after_request
def add_perf_headers(response):
    try:
        # Long-cache static assets (overrides Werkzeug's send_file no-cache)
        path = (request.path or '').rsplit('?', 1)[0]
        ext = path.rsplit('.', 1)[-1].lower() if '.' in path else ''
        if ext in _STATIC_EXTS:
            response.headers['Cache-Control'] = 'public, max-age=2592000'

        # gzip compress text responses when the client supports it
        accepts_gzip = 'gzip' in request.headers.get('Accept-Encoding', '').lower()
        can_gzip = (request.method in ('GET', 'POST')
                    and accepts_gzip
                    and 200 <= response.status_code < 300
                    and not response.headers.get('Content-Encoding'))
        if can_gzip:
            ctype = (response.content_type or '').split(';')[0].strip().lower()
            if ctype in _COMPRESSIBLE:
                response.direct_passthrough = False
                data = response.get_data()
                if len(data) >= 500:
                    buf = BytesIO()
                    with gzip.GzipFile(mode='wb', fileobj=buf, compresslevel=6) as gz:
                        gz.write(data)
                    out = buf.getvalue()
                    response.set_data(out)
                    response.headers['Content-Encoding'] = 'gzip'
                    response.headers['Content-Length'] = str(len(out))
                    vary = response.headers.get('Vary')
                    if not vary:
                        response.headers['Vary'] = 'Accept-Encoding'
                    elif 'accept-encoding' not in vary.lower():
                        response.headers['Vary'] = vary + ', Accept-Encoding'
    except Exception:
        log.warning(Logs.fileline() + ' : perf after_request skipped; response left unmodified')
    return response


LANG_SELECT = {'''
assert anchor in s, "before_request/LANG_SELECT anchor not found"
s = s.replace(anchor, block, 1)
open(p, 'w', encoding='utf-8').write(s)
print("  added gzip + caching")
PYEOF

echo "=== syntax check (container python3.11) ==="
podman exec labbook-bundle-app python3.11 -c "import ast; ast.parse(open('/home/apps/labbook_FE/labbook_FE/app/__init__.py').read()); print('  syntax OK')"

echo "=== 2/3 simplify .htaccess (app now handles compression+caching) ==="
cat > "$HT" <<'HTEOF'
RewriteEngine On
<IfModule mod_headers.c>
RequestHeader set X-Forwarded-Proto "https"
</IfModule>
RewriteRule ^\.well-known/ - [L]
RewriteCond %{HTTPS} off
RewriteRule .* https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]
RewriteRule ^/?$ https://%{HTTP_HOST}/sigl [R=301,L]
RewriteRule ^(.*)$ http://127.0.0.1:5000/$1 [P,L]
HTEOF
chown aslmacademy:aslmacademy "$HT"
echo "  .htaccess simplified"

echo "=== 3/3 recreate bundle (reload __init__.py) ==="
cd "$R" && bash deploy/labbook-bundle.sh up
sleep 12
echo "=== verify (internal loopback) ==="
echo -n "login HTML  : "; curl -s -D - -o /dev/null -H 'Accept-Encoding: gzip' http://127.0.0.1:5000/sigl | grep -i '^content-encoding' || echo "no gzip"
echo "  plain $(curl -s -o /dev/null -w '%{size_download}' http://127.0.0.1:5000/sigl) -> gzip $(curl -s -o /dev/null -w '%{size_download}' -H 'Accept-Encoding: gzip' http://127.0.0.1:5000/sigl) bytes"
echo -n "bootstrap   : "; curl -s -D - -o /dev/null -H 'Accept-Encoding: gzip' http://127.0.0.1:5000/sigl/static/vendor/bootstrap/css/bootstrap.min.css | grep -iE '^(content-encoding|cache-control)' | tr '\n' ' '; echo
echo "  plain $(curl -s -o /dev/null -w '%{size_download}' http://127.0.0.1:5000/sigl/static/vendor/bootstrap/css/bootstrap.min.css) -> gzip $(curl -s -o /dev/null -w '%{size_download}' -H 'Accept-Encoding: gzip' http://127.0.0.1:5000/sigl/static/vendor/bootstrap/css/bootstrap.min.css) bytes"
echo -n "demo panels : "; curl -s http://127.0.0.1:5000/sigl | grep -c demo-accts
echo -n "language    : "; curl -s http://127.0.0.1:5000/sigl | grep -oiE 'Logging in|Ouverture de session' | head -1
echo "ALL DONE"
