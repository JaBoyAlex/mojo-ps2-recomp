#!/bin/sh
# Invoked by the native launcher; arguments remain separate, including Unicode paths.
set -eu
root=$1
shift
case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) target=aarch64-apple-darwin; hash=1afd3983237c2a10277345f235be730e9cb49a123e0574ed252dbf3a841a24e4 ;;
    Darwin-x86_64) target=x86_64-apple-darwin; hash=a46bcdeecd28ba253522b321dcb3806da1b0ff581479fc1d27e9613e3ac44764 ;;
    Linux-x86_64) target=x86_64-unknown-linux-gnu; hash=50c774f6674740739f791c05a9177ed03e2fe02abebda9bca3512eb7309b37cc ;;
    *) echo 'Unsupported native platform.' >&2; exit 21 ;;
esac
case "$target" in
    *apple*) state="$HOME/Library/Application Support/MOJO Recomp" ;;
    *) state="$root/userdata" ;;
esac
cache="$state/cache"
python="$cache/python-20261110-$target/python/bin/python3"
python_home="$cache/python-20261110-$target"
if [ ! -x "$python" ] || [ ! -f "$python_home/.complete" ]; then
    mkdir -p "$cache"
    lock="$cache/python-bootstrap.lock"
    waited=0
    while ! mkdir "$lock" 2>/dev/null; do
        owner=$(cat "$lock/pid" 2>/dev/null || true)
        if [ -n "$owner" ] && ! kill -0 "$owner" 2>/dev/null; then
            rm -f "$lock/pid"; rmdir "$lock" 2>/dev/null || true
        fi
        waited=$((waited + 1))
        if [ "$waited" -ge 600 ]; then echo 'Another setup is using the Python cache. Close it and retry.' >&2; exit 24; fi
        sleep 1
    done
    trap 'rm -f "$lock/pid"; rmdir "$lock" 2>/dev/null || true' EXIT
    trap 'exit 23' INT TERM
    echo $$ > "$lock/pid"
    if [ ! -x "$python" ] || [ ! -f "$python_home/.complete" ]; then
        echo 'progress 0.00 Downloading verified native Python'
        archive="$cache/python-$target.tar.gz"
        url="https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.13.18%2B20261110-$target-install_only.tar.gz"
        curl --fail --location --silent --show-error --retry 3 --connect-timeout 30 --max-time 600 "$url" -o "$archive.download" || exit 21
        if command -v sha256sum >/dev/null 2>&1; then
            actual=$(sha256sum "$archive.download" | cut -d' ' -f1)
        else
            actual=$(shasum -a 256 "$archive.download" | cut -d' ' -f1)
        fi
        if [ "$actual" != "$hash" ]; then echo 'Python checksum mismatch.' >&2; exit 21; fi
        mv "$archive.download" "$archive"
        staging=$(mktemp -d "$cache/python-unpack.XXXXXX")
        tar -xzf "$archive" -C "$staging" || exit 21
        "$staging/python/bin/python3" -I -c 'import argparse, hashlib, json, ssl, zipfile' || exit 21
        touch "$staging/.complete"
        if [ -e "$python_home" ]; then mv "$python_home" "$python_home.incomplete.$$"; fi
        mv "$staging" "$python_home"
    fi
    rm -f "$lock/pid"; rmdir "$lock"
    trap - EXIT INT TERM
fi
# Use the OS certificate bundle with portable OpenSSL; never disable verification.
if [ -z "${SSL_CERT_FILE:-}" ]; then
    for certificates in /etc/ssl/certs/ca-certificates.crt /etc/ssl/cert.pem; do
        if [ -f "$certificates" ]; then SSL_CERT_FILE=$certificates; export SSL_CERT_FILE; break; fi
    done
fi
exec "$python" "$root/builder/bootstrap_native.py" --root "$root" "$@"
