#!/usr/bin/env bash
set -euo pipefail
test "$(id -u)" = 0
test ! -e /etc/nginx/sites-available/usjunkcars.si
install -d -m 755 /usr/local/lib/usjunkcars /srv/usjunkcars/holding /etc/usjunkcars
install -m 755 /tmp/usjunkcars-setup/receive-release.py /usr/local/lib/usjunkcars/receive-release.py
install -m 644 /tmp/usjunkcars-setup/holding.html /srv/usjunkcars/holding/index.html

# An isolated Node runtime leaves all existing websites' Node/PM2 versions alone.
runtime_tmp=$(mktemp -d)
trap 'rm -rf "$runtime_tmp"' EXIT
cd "$runtime_tmp"
archive=node-v24.22.0-linux-x64.tar.xz
curl -fsSLO "https://nodejs.org/dist/v24.22.0/$archive"
curl -fsSLO https://nodejs.org/dist/v24.22.0/SHASUMS256.txt
awk -v file="$archive" '$2 == file' SHASUMS256.txt | sha256sum -c -
install -d /usr/local/lib/usjunkcars/node
tar -xJf "$archive" --strip-components=1 -C /usr/local/lib/usjunkcars/node

for branch in dev main; do
  user="usjunkcars-$branch"
  if ! id "$user" >/dev/null 2>&1; then useradd --system --create-home --shell /bin/sh "$user"; fi
  home=$(getent passwd "$user" | cut -d: -f6)
  chown root:root "$home"
  chmod 755 "$home"
  install -d -m 755 "$home/.ssh"
  install -d -o "$user" -g "$user" -m 755 "/srv/usjunkcars/$branch" "/srv/usjunkcars/$branch/releases"
  install -d -o "$user" -g "$user" -m 750 "/srv/usjunkcars/$branch/cache"
  port=3401; origin=https://dev.usjunkcars.si; environment=development
  if [ "$branch" = main ]; then port=3400; origin=https://usjunkcars.si; environment=production; fi
  printf 'NODE_ENV=production\nHOSTNAME=127.0.0.1\nPORT=%s\nAPP_ENV=%s\nSITE_URL=%s\n' "$port" "$environment" "$origin" > "/etc/usjunkcars/$branch.env"
  chown "root:$user" "/etc/usjunkcars/$branch.env"
  chmod 640 "/etc/usjunkcars/$branch.env"
  cat > "/etc/systemd/system/usjunkcars-$branch.service" <<EOF
[Unit]
Description=USJunkCars $environment Next.js
After=network.target
ConditionPathExists=/srv/usjunkcars/$branch/current/apps/web/server.js
[Service]
User=$user
Group=$user
WorkingDirectory=/srv/usjunkcars/$branch/current
EnvironmentFile=/etc/usjunkcars/$branch.env
EnvironmentFile=/srv/usjunkcars/$branch/current/.release.env
ExecStart=/usr/local/lib/usjunkcars/node/bin/node /srv/usjunkcars/$branch/current/apps/web/server.js
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/srv/usjunkcars/$branch/cache
MemoryMax=768M
CPUQuota=100%
UMask=0027
[Install]
WantedBy=multi-user.target
EOF
  printf '%s ALL=(root) NOPASSWD: /usr/bin/systemctl restart usjunkcars-%s.service\n' "$user" "$branch" > "/etc/sudoers.d/usjunkcars-$branch"
  chmod 440 "/etc/sudoers.d/usjunkcars-$branch"
  visudo -cf "/etc/sudoers.d/usjunkcars-$branch"
done
systemctl daemon-reload
systemctl enable usjunkcars-dev.service usjunkcars-main.service

cat > /etc/nginx/sites-available/usjunkcars.si <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name usjunkcars.si www.usjunkcars.si dev.usjunkcars.si;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 503 "USJunkCars.si is not launched yet.\n"; }
    add_header X-Robots-Tag "noindex, nofollow" always;
}
EOF
ln -s /etc/nginx/sites-available/usjunkcars.si /etc/nginx/sites-enabled/usjunkcars.si
nginx -t
systemctl reload nginx
/usr/local/lib/usjunkcars/node/bin/node --version
