# LabBook self-contained bundle (`labbook-bundle.sh`)

Runs LabBook **and its own MariaDB** as one Podman pod that listens **only on a
loopback port** (default `127.0.0.1:5000`). This is the deployment shape for a
**cPanel/WHM server**: it never uses host ports 80/443 and never touches the
system MySQL, so it coexists with existing websites. You expose it by pointing a
cPanel subdomain at the loopback port via reverse proxy + AutoSSL.

> Tested locally on WSL2/Podman: app + bundled DB come up clean, `init/version`
> returns 200, no crash-loop. Same unit deploys to AlmaLinux 8 + cPanel.

## Run it
```bash
# from the repo root, as root (rootful podman)
podman image exists localhost/labbook-python:latest \
  || gunzip -c backup/labbook-python-*.tar.gz | podman load   # or: make devbuild

BIND=127.0.0.1:5000 ./deploy/labbook-bundle.sh up      # start (seeds SIGL on first run)
./deploy/labbook-bundle.sh status                       # show pod/containers
./deploy/labbook-bundle.sh logs                         # tail app logs
./deploy/labbook-bundle.sh down                         # stop (keeps the DB volume)
```
- A random DB password is generated once into `deploy/runtime/db_credentials.env`
  (git-ignored). The DB lives in the `labbook_db_data` volume; `/storage` and logs
  persist in `labbook_storage` / `labbook_logs`.
- The app is at `http://127.0.0.1:5000/sigl`.

## Expose via a cPanel subdomain (reverse proxy + HTTPS)
1. In **cPanel → Domains**, create the subdomain you want (e.g. `labbook.example.org`),
   pointing DNS (A record) at this server's IP.
2. In **cPanel → SSL/TLS Status**, run **AutoSSL** for that subdomain (free Let's Encrypt).
3. In **WHM → Apache Configuration → Include Editor**, add a *Post-VirtualHost Include*
   for the subdomain (HTTPS vhost) so Apache proxies to the bundle:
   ```apache
   ProxyPreserveHost On
   RequestHeader set X-Forwarded-Proto "https"
   ProxyPass        / http://127.0.0.1:5000/
   ProxyPassReverse / http://127.0.0.1:5000/
   RedirectMatch ^/$ /sigl
   ```
   (LabBook serves under the `/sigl` path; the last line sends the bare domain there.)
4. Rebuild + restart Apache when prompted.

## Auto-start on boot (systemd)
```bash
# generate a unit for the pod after it's running
podman generate systemd --new --files --name labbook-bundle
# install & enable (example for the app container unit set)
cp container-labbook-bundle*.service pod-labbook-bundle.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now pod-labbook-bundle.service
```

## Security checklist before sharing the URL
- [ ] **Change the demo web logins** (`root`/`root` and the other demo accounts) in
      **Administratif → Gestion des utilisateurs**.
- [ ] Firewall: only 80/443 inbound (the bundle's port stays on loopback).
- [ ] Keep `deploy/runtime/` private (it holds the DB password) — already git-ignored.
- [ ] Back up the `labbook_db_data` volume regularly (`podman exec labbook-bundle-db mariadb-dump ...`).

See `../DEPLOY.md` for the non-cPanel (dedicated host, native MariaDB) variant.
