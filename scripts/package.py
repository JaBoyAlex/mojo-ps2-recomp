"""Build an archive from an explicit source allowlist and two fresh helper binaries."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'scripts/verify_publication.py')],check=True)
files=json.loads((root/'publication-files.json').read_text())
dest=root/'dist'
dest.mkdir(exist_ok=True)
archive=dest/'MOJO-Recomp-v1.0.0-rc.5-Windows-x64.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in sorted(files): z.write(root/name,name)
    for name in ('MOJO.exe','chd_to_iso.exe'): z.write(root/'build/helpers'/name,name)
subprocess.run([sys.executable,str(root/'scripts/verify_publication.py'),'--archive',str(archive)],check=True)
archive.with_suffix('.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
print('Created '+archive.name)
