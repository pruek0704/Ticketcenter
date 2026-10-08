#!/bin/sh
set -eu
mkdir -p /etc/nginx/tls
if [ ! -f /etc/nginx/tls/cert.pem ] || [ ! -f /etc/nginx/tls/key.pem ]; then
  openssl req -x509 -newkey rsa:2048 -nodes -days 7 -keyout /etc/nginx/tls/key.pem -out /etc/nginx/tls/cert.pem -subj '/CN=localhost'
fi
sed -i "s/API_HOST_PLACEHOLDER/${API_HOST:-api}/g; s/DNS_RESOLVER_PLACEHOLDER/${DNS_RESOLVER:-127.0.0.11}/g" /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'
