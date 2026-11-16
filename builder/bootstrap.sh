#!/bin/sh
# Invoked by the native launcher; arguments remain separate, including Unicode paths.
set -eu
root=$1
shift
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Python 3.9 or newer is required. On macOS install Apple Command Line Tools; on Linux install python3.' >&2
    exit 21
fi
exec python3 "$root/builder/bootstrap_native.py" --root "$root" "$@"
