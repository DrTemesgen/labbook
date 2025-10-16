#!/bin/bash
#
# Start gunicorn to serve the application in production mode
#
# PhB, 08/10/14
# PHM, 01/10/15 -> adaptation aux serveurs d'applications Web (amicare, borne, ...)
# AlC, 18/11/19 -> adaptation pour le projet labbook

# PHM le 19/11/19 : Passage Apache->gunicorn via port 8081
HOST="localhost"
PORT="8081"

#############
# Functions #
#############
#
# Display use
#
usage()
{
echo
echo "Run Gunicorn Labbook FRONT END"
echo
echo "Use :"
echo "  $0 -h"
echo "  $0 -r"
echo
echo "Options:"
echo "  -h                 This help"
echo "  -r                 Add reload option"
echo
exit 2
}

######################
# START              #
######################
opt_reload=""

while getopts "hr" option
do
    case "$option" in
    h)
    usage
    ;;

    r)
    opt_reload="--reload"
    ;;

    *)
    echo "option $option unknown"
    usage
    ;;
    esac
done

test "$LABBOOK_DEBUG" -eq 1 && opt_reload="--reload"

# Application name
APP_NAME=labbook_FE

HOME_APP=/home/apps/$APP_NAME
APP_DIR=${HOME_APP}/${APP_NAME}
VENV_DIR=${APP_DIR}/venv
LOGS_DIR=/home/apps/logs
GUNICORN_DIR=${HOME_APP}/gunicorn
GUNICORN_TIMEOUT=120

SHARED_SECRET=/storage/key/secret_key.py
OAUTH_SHARED="$(dirname "$SHARED_SECRET")/oauth_client_secret.py"

# shellcheck disable=SC1091
source ${VENV_DIR}/bin/activate

# create Gunicorn directory if necessary
mkdir -p ${GUNICORN_DIR}
mkdir -p ${LOGS_DIR}
mkdir -p "$(dirname "$SHARED_SECRET")"

# Generate shared SECRET_KEY if missing
if [ ! -f "$SHARED_SECRET" ]; then
    echo "Generating shared SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    echo "SECRET_KEY = '$SECRET_KEY'" > "$SHARED_SECRET"
else
    echo "Shared SECRET_KEY file already exists."
fi

# Operating environment
export LOCAL_SETTINGS=${HOME_APP}/local_settings.py

# if local_settings file doesnt exist we create one
# from local_settings.py.sample in app directory
# AlC 10/07/2025 comment replace by generate secret key
# test -f $LOCAL_SETTINGS || {
#     echo "$LOCAL_SETTINGS not found, local_settings.py file create"
#
#     cp ${APP_DIR}/local_settings.py.sample $LOCAL_SETTINGS || exit 1
# }

LOCAL_SETTINGS_SAMPLE=${APP_DIR}/local_settings.py.sample

# Create local_settings.py if missing, inject shared SECRET_KEY
if [ ! -f "$LOCAL_SETTINGS" ]; then
    echo "Creating $LOCAL_SETTINGS from sample and injecting shared SECRET_KEY"

    cp "$LOCAL_SETTINGS_SAMPLE" "$LOCAL_SETTINGS" || exit 1

    # Replace the SECRET_KEY line with the shared one
    sed -i "/^SECRET_KEY/c\\$(cat $SHARED_SECRET)" "$LOCAL_SETTINGS"
fi

# --- start OAuth FE client secret block ---
PLACEHOLDER="replace-me-with-random-secret-key"
OAUTH_SECRET=""

read_shared_secret() {
  python3 - <<'PY'
ns={}
try:
    with open('/storage/key/oauth_client_secret.py','r') as f:
        exec(f.read(), ns)
    v = ns.get('OAUTH_CLIENT_SECRET','').strip()
    print(v)
except Exception:
    print('')
PY
}

read_local_secret() {
  python3 - <<PY
ns={}
try:
    with open("${LOCAL_SETTINGS}","r") as f:
        exec(f.read(), ns)
    v = ns.get('OAUTH_CLIENT_SECRET','').strip()
    print(v)
except Exception:
    print('')
PY
}

# 1) Try shared secret first
if [ -f "$OAUTH_SHARED" ]; then
    OAUTH_SECRET="$(read_shared_secret)"
fi

# 2) Fallback to local_settings.py if present and not placeholder
if [ -z "$OAUTH_SECRET" ]; then
    EXISTING_LOCAL="$(read_local_secret)"
    if [ -n "$EXISTING_LOCAL" ] && [ "$EXISTING_LOCAL" != "$PLACEHOLDER" ]; then
        echo "Reusing OAUTH_CLIENT_SECRET from local_settings.py"
        OAUTH_SECRET="$EXISTING_LOCAL"
        echo "OAUTH_CLIENT_SECRET = '${OAUTH_SECRET}'" > "$OAUTH_SHARED"
    fi
fi

# 3) Generate if still empty
if [ -z "$OAUTH_SECRET" ]; then
    echo "Generating FE OAuth client secret..."
    OAUTH_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    echo "OAUTH_CLIENT_SECRET = '$OAUTH_SECRET'" > "$OAUTH_SHARED"
fi

# 4) Ensure local_settings.py has the chosen secret and client_id
if grep -qE "^[[:space:]]*OAUTH_CLIENT_SECRET[[:space:]]*=" "$LOCAL_SETTINGS"; then
    sed -i "s|^[[:space:]]*OAUTH_CLIENT_SECRET[[:space:]]*=.*|OAUTH_CLIENT_SECRET = '${OAUTH_SECRET}'|" "$LOCAL_SETTINGS"
else
    printf "\nOAUTH_CLIENT_SECRET = '%s'\n" "$OAUTH_SECRET" >> "$LOCAL_SETTINGS"
fi

if grep -qE "^[[:space:]]*OAUTH_CLIENT_ID[[:space:]]*=" "$LOCAL_SETTINGS"; then
    sed -i "s|^[[:space:]]*OAUTH_CLIENT_ID[[:space:]]*=.*|OAUTH_CLIENT_ID = 'labbook-FE'|" "$LOCAL_SETTINGS"
else
    printf "OAUTH_CLIENT_ID = 'labbook-FE'\n" >> "$LOCAL_SETTINGS"
fi

export LABBOOK_OAUTH_FE_SECRET="${OAUTH_SECRET}"
# --- end OAuth FE client secret block ---

cd ${APP_DIR} || exit 1

# Gunicorn is installed in the virtual environment
# When started by supervisord, exec is necessary for the signals to reach gunicorn.
# Another approach with catched signals is described here :
# http://serverfault.com/questions/425132/controlling-tomcat-with-supervisor
exec gunicorn \
    $opt_reload \
    --timeout ${GUNICORN_TIMEOUT} \
    --pid ${GUNICORN_DIR}/gunicorn.pid \
    --bind ${HOST}:${PORT} \
    --access-logfile ${LOGS_DIR}/gunicorn-FE-access.log \
    --access-logformat "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" \"%({uniqueid}i)s\"" \
    --error-logfile ${LOGS_DIR}/gunicorn-FE-error.log \
    rungunicorn:app > ${LOGS_DIR}/gunicorn.out 2>&1
