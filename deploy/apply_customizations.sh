#!/bin/bash
set -euo pipefail
R=/opt/labbook
FE="$R/labbook_FE/app"
TS=$(date +%s)
echo "=== backup FE files ==="
cp "$FE/templates/login.html" "$FE/templates/login.html.bak.$TS"
cp "$FE/__init__.py" "$FE/__init__.py.bak.$TS"

echo "=== 1/6 login.html: insert demo-account panels ==="
python3 - "$FE/templates/login.html" <<'PYEOF'
import sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
block='''        <style>
        .demo-accts{position:fixed;top:150px;width:300px;background:rgba(255,255,255,.93);border:1px solid #cfcfcf;border-radius:10px;padding:14px 16px;box-shadow:0 2px 12px rgba(0,0,0,.18);font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;z-index:50}
        .demo-accts h3{margin:0 0 6px;font-size:15px;color:#3a7d34}
        .demo-accts .pw{background:#eef6ec;border:1px solid #cde3c8;border-radius:6px;padding:5px 8px;margin:6px 0 10px}
        .demo-accts table{width:100%;border-collapse:collapse}
        .demo-accts td{padding:3px 4px;border-bottom:1px solid #eee}
        .demo-accts td.u{font-family:monospace;font-weight:bold;color:#b5402a}
        .demo-left{left:24px}
        .demo-right{right:24px}
        @media(max-width:1100px){.demo-accts{position:static;width:auto;margin:12px auto;max-width:520px}}
        </style>
        <div class="demo-accts demo-left">
            <h3>Demo logins</h3>
            <div class="pw">For each, the <b>password = the login</b></div>
            <table>
                <tr><td>Administrator</td><td class="u">root</td></tr>
                <tr><td>Biologist</td><td class="u">biologiste</td></tr>
                <tr><td>Technician</td><td class="u">technicien</td></tr>
                <tr><td>Secretary</td><td class="u">secretaire</td></tr>
                <tr><td>Prescriber</td><td class="u">prescripteur</td></tr>
                <tr><td>Qualitician</td><td class="u">qualiticien</td></tr>
            </table>
        </div>
        <div class="demo-accts demo-right">
            <h3>More demo logins</h3>
            <div class="pw">For each, the <b>password = the login</b></div>
            <table>
                <tr><td>Laboratory</td><td class="u">lab</td></tr>
                <tr><td>Stock management</td><td class="u">stock</td></tr>
                <tr><td>Adv. technician</td><td class="u">techav</td></tr>
                <tr><td>Qualitician-Technician</td><td class="u">techq</td></tr>
                <tr><td>Adv. secretary</td><td class="u">secrav</td></tr>
            </table>
        </div>
'''
if 'demo-accts' not in s:
    assert '        <footer>' in s, "footer anchor missing"
    s=s.replace('        <footer>', block+'        <footer>',1)
    open(p,'w',encoding='utf-8').write(s); print("  inserted")
else: print("  already present")
PYEOF

echo "=== 2/6 __init__.py: force English UK ==="
python3 - "$FE/__init__.py" <<'PYEOF'
import sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
if 'Forced system default language' in s:
    print("  already forced"); sys.exit(0)
og='''    log.info(Logs.fileline() + ' : LANG = ' + str(os.environ['LANG']))
    lang = request.accept_languages.best_match(list(LANGUAGES.keys()), default='fr_FR')
    if not session or 'lang' not in session:
        session['lang'] = lang
        session.modified = True
        log.info(Logs.fileline() + ' :default lang=' + str(lang))
    elif session and 'lang' in session:
        lang = session['lang']
        log.info(Logs.fileline() + ' :session lang=' + str(lang))
    return lang'''
ng='''    log.info(Logs.fileline() + ' : LANG = ' + str(os.environ['LANG']))
    # Forced system default language: English (UK)
    lang = 'en_GB'
    session['lang'] = lang
    session.modified = True
    return lang'''
ol='''    lang = app.config.get('BABEL_DEFAULT_LOCALE')
    if session and 'lang' in session:
        lang = session['lang']
        log.info(Logs.fileline() + ' : lang = ' + lang)

        session['lang_select'] = LANG_SELECT.get(lang, 'FR')
        if lang in EU_FORMAT_LANGS:
            session['date_format'] = Constants.cst_date_eu
            session['dt_format']   = Constants.cst_dt_eu_HM
        else:
            session['date_format'] = Constants.cst_date_us
            session['dt_format']   = Constants.cst_dt_us_HM

        session.modified = True

    return dict(locale=lang)'''
nl='''    # Forced system default language: English (UK)
    lang = 'en_GB'
    session['lang'] = lang
    session['lang_select'] = LANG_SELECT.get(lang, 'UK')
    session['date_format'] = Constants.cst_date_eu
    session['dt_format']   = Constants.cst_dt_eu_HM
    session.modified = True
    return dict(locale=lang)'''
assert og in s, "get_locale block not found"
assert ol in s, "locale block not found"
open(p,'w',encoding='utf-8').write(s.replace(og,ng,1).replace(ol,nl,1)); print("  forced en_GB")
PYEOF

echo "=== 3/6 add FE mounts to launcher ==="
B="$R/deploy/labbook-bundle.sh"
grep -q 'app/templates/login.html:/home/apps' "$B" || sed -i 's|default_settings.py:ro,Z"|default_settings.py:ro,Z" -v "$REPO/labbook_FE/app/templates/login.html:/home/apps/labbook_FE/labbook_FE/app/templates/login.html:ro,Z"|' "$B"
grep -q 'app/__init__.py:/home/apps' "$B" || sed -i 's|app/templates/login.html:ro,Z"|app/templates/login.html:ro,Z" -v "$REPO/labbook_FE/app/__init__.py:/home/apps/labbook_FE/labbook_FE/app/__init__.py:ro,Z"|' "$B"
grep -oE 'labbook_FE/app[^"]*:ro,Z' "$B"

echo "=== 4/6 reset demo passwords = login name ==="
. "$R/deploy/runtime/db_credentials.env"
podman exec -i labbook-bundle-app python3.11 - > /tmp/pwreset.sql <<'PYEOF'
import hashlib, os
def gen(pwd):
    salt=hashlib.sha1(os.urandom(32)).hexdigest()
    L=len(pwd); st=L-1; e=40-L+st
    q=pwd+salt[st:e]
    return hashlib.sha1(hashlib.md5(q.encode()).hexdigest().encode()).hexdigest()+':'+salt
for u in ['root','biologiste','technicien','secretaire','prescripteur','qualiticien','lab','stock','techav','techq','secrav']:
    print("UPDATE sigl_user_data SET password=%r WHERE username=%r;" % (gen(u), u))
PYEOF
podman exec -i labbook-bundle-db mariadb -ulabbook -p"$DB_PASS" SIGL < /tmp/pwreset.sql
echo "  done"

echo "=== 5/6 compression + caching for mobile (.htaccess) ==="
cat > /home/aslmacademy/labbook.aslmacademy.org/.htaccess <<'HTEOF'
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/plain text/css text/xml application/javascript application/x-javascript application/json image/svg+xml application/xml application/rss+xml
</IfModule>
RewriteEngine On
<IfModule mod_headers.c>
RequestHeader set X-Forwarded-Proto "https"
</IfModule>
RewriteRule ^\.well-known/ - [L]
RewriteCond %{HTTPS} off
RewriteRule .* https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]
RewriteRule ^/?$ https://%{HTTP_HOST}/sigl [R=301,L]
RewriteRule \.(css|js|png|jpe?g|gif|ico|woff2?|svg|ttf|eot)$ - [E=LBKSTATIC:1]
<IfModule mod_headers.c>
Header always unset Cache-Control env=LBKSTATIC
Header always set Cache-Control "public, max-age=2592000" env=LBKSTATIC
</IfModule>
RewriteRule ^(.*)$ http://127.0.0.1:5000/$1 [P,L]
HTEOF
chown aslmacademy:aslmacademy /home/aslmacademy/labbook.aslmacademy.org/.htaccess
echo "  done"

echo "=== 6/6 recreate bundle (applies the FE mounts) ==="
cd "$R" && bash deploy/labbook-bundle.sh up
sleep 12
echo "=== verify ==="
echo -n "demo panels on login page: "; curl -s http://127.0.0.1:5000/sigl | grep -c demo-accts
echo -n "login page language: "; curl -s http://127.0.0.1:5000/sigl | grep -oiE 'Logging in|Ouverture de session' | head -1
echo "ALL DONE"
