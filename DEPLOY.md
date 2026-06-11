# Deploying LabBook on a Linux VPS (root/SSH)

This is a private fork of [fondationmerieux/labbook_python](https://github.com/fondationmerieux/labbook_python)
(LabBook **3.6.19**, GPL v2) with deployment notes for running it on our own server so the
team can use it from a browser. For local Windows/WSL development see `RUN_LABBOOK.md` in the
deployment notes; this file is the **server** guide.

> LabBook is a containerized app: Apache + Python (gunicorn) FE/BE + a job runner +
> LibreOffice/wkhtmltopdf + a MariaDB database. It needs a real Linux host with **root**
> (a VPS or dedicated server). It will **not** run on shared cPanel hosting.

---

## 1. Prerequisites on the server (run as root)

Debian/Ubuntu:
```bash
apt-get update
apt-get install -y podman slirp4netns make git rsync mariadb-server mariadb-client
```
RHEL/AlmaLinux/Rocky:
```bash
dnf install -y podman slirp4netns make git rsync mariadb-server
systemctl enable --now mariadb
```

## 2. Get the code
```bash
git clone <YOUR_PRIVATE_REPO_URL> /opt/labbook
cd /opt/labbook
```

## 3. Configure MariaDB
Create `/etc/mysql/mariadb.conf.d/99-labbook.cnf` (Debian) or `/etc/my.cnf.d/labbook.cnf` (RHEL):
```ini
[mariadb]
sql_mode=''
# Bind to localhost + the podman bridge only. Do NOT expose 3306 to the internet.
bind-address=0.0.0.0
```
```bash
systemctl restart mariadb
```

Create the database user. The app makes an **import-time** DB call using the credentials in
`labbook_BE/default_settings.py` (`root`/`root`/`10.88.0.1`) *before* it reads environment
overrides, so that user must be reachable from the Podman bridge subnet `10.88.%.%`:
```sql
-- minimal (matches shipped defaults; bridge-internal only)
CREATE USER root@'10.88.%.%' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON *.* TO root@'10.88.%.%' WITH GRANT OPTION;
-- application user for the request path
CREATE USER labbook@'10.88.%.%' IDENTIFIED BY 'CHANGE_ME_STRONG';
GRANT ALL PRIVILEGES ON *.* TO labbook@'10.88.%.%';
FLUSH PRIVILEGES;
```
> **Harden (recommended):** instead of the weak `root/root`, edit `labbook_BE/default_settings.py`
> on the server to `DB_USER='labbook'`, `DB_PWD='CHANGE_ME_STRONG'`, `DB_HOST='10.88.0.1'`, and
> create only the `labbook@'10.88.%.%'` user above. Then no weak/root account exists. (Do not commit this edit.)

## 4. Config file `~/.config/labbook.conf`
```ini
LABBOOK_DB_USER=labbook
LABBOOK_DB_PWD=CHANGE_ME_STRONG
LABBOOK_DB_NAME=SIGL
LABBOOK_DB_HOST=10.88.0.1
LABBOOK_DEBUG=0
```

## 5. Initialize the database (demo data) and build
```bash
make dbinit       # loads etc/sql/demo_dump.sql into the SIGL database
make devbuild     # builds the container image (several minutes)
```
> To skip the build, copy the prebuilt `labbook-python-*.tar.gz` to the server and
> `gunzip -c labbook-python-*.tar.gz | podman load`.

## 6. Run on the default bridge network (important)
The bundled `make devrun` creates the pod with `slirp4netns`, where the DB host `10.88.0.1`
is unreachable and the backend crash-loops. Pre-create the pod on the **default bridge**
(where `10.88.0.1` is the real host gateway) so `make devrun` reuses it:
```bash
podman pod create --name=labbook --network=podman --publish=127.0.0.1:5000:80
make devrun
```
The app now listens on `127.0.0.1:5000` (loopback only — we put HTTPS in front of it next).

## 7. Put it behind your domain with HTTPS
Point a DNS record (e.g. `labbook.yourcompany.com`) at the server, then use a reverse proxy
with a free Let's Encrypt certificate. Example with Caddy (simplest):
```bash
# /etc/caddy/Caddyfile
labbook.yourcompany.com {
    reverse_proxy 127.0.0.1:5000
}
```
(or use nginx + certbot if you prefer). Open only ports 80/443 in the firewall.

## 8. Security checklist BEFORE sharing the URL
- [ ] **Change the LabBook web logins** — the demo seeds `root`/`root` (and other demo
      accounts). Log in, then **Administratif → Gestion des utilisateurs** and reset passwords.
- [ ] Firewall: allow only 80/443 inbound; block 3306 (MariaDB) from the internet.
- [ ] Use a strong DB password (`CHANGE_ME_STRONG` above).
- [ ] `LABBOOK_DEBUG=0` in production (disables gunicorn auto-reload).
- [ ] Set up regular DB backups (`mysqldump SIGL`) and `/storage` volume backups.

## 9. Start/stop/status
```bash
make devrun     # start
make devstop    # stop
podman exec labbook_python supervisorctl -c /home/supervisor/etc/supervisor.conf status
```

---
*Provenance: forked from fondationmerieux/labbook_python at v3.6.19. Licensed under GPL v2 (see `LICENSE.md`).*
