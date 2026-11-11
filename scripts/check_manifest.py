"""Validate against a SHA-256-pinned official SDK schema, not an invented subset."""
import hashlib
import json
from pathlib import Path
import urllib.request
import jsonschema
request=urllib.request.Request('https://recomplauncher.com/schema/recomplauncher.json',headers={'User-Agent':'Mozilla/5.0'})
schema=urllib.request.urlopen(request,timeout=30).read()
# Both official snapshots were reviewed on 2026-11-11. The second adds optional
# NVIDIA DLSS runtime inputs; none of this project's fields change. CDN caches
# may serve either snapshot while the SDK update rolls out.
reviewed={
    'b962fe1c3d3c7e916c0032efd8259c36f0cd4a7fdb63ea6d858166a72750c217',
    '0946d89093460d0aa60f4877e486d3c65ae4dd3ee251b500db98b4fc626632f3',
}
if hashlib.sha256(schema).hexdigest() not in reviewed:
    raise SystemExit('SDK schema changed; review before updating the pinned hash.')
root=Path(__file__).resolve().parents[1]
jsonschema.validate(json.loads((root/'recomplauncher.json').read_text(encoding='utf-8')),json.loads(schema))
print('PASS: official RecompLauncher JSON schema')
