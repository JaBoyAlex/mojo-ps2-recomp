"""Independent native secret scan plus the fail-closed publication gate."""
import hashlib
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
HASHES={
    'linux_x64':'551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb',
    'darwin_arm64':'b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5',
    'darwin_x64':'dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709',
}

def main():
    system='darwin' if sys.platform=='darwin' else 'linux'
    arch='arm64' if platform.machine().lower() in ('aarch64','arm64') else 'x64'
    key=system+'_'+arch
    url='https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_'+key+'.tar.gz'
    with tempfile.TemporaryDirectory() as folder:
        work=Path(folder);archive=work/'scanner.tar.gz'
        with urllib.request.urlopen(url,timeout=60) as source:archive.write_bytes(source.read())
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=HASHES[key]:raise SystemExit('Gitleaks checksum mismatch')
        with tarfile.open(archive) as tar:
            member=tar.getmember('gitleaks')
            if not member.isfile():raise SystemExit('Invalid scanner archive')
            scanner=work/'gitleaks';scanner.write_bytes(tar.extractfile(member).read());scanner.chmod(0o755)
        subprocess.run([sys.executable,str(ROOT/'scripts/verify_publication.py'),'--git'],check=True)
        subprocess.run([str(scanner),'git',str(ROOT),'--log-opts=--all','--redact=100','--no-banner'],check=True)
        for archive in (ROOT/'dist').glob('*native-preview*'):
            if not archive.name.endswith(('.zip','.tar.gz')): continue
            subprocess.run([sys.executable,str(ROOT/'scripts/verify_publication.py'),'--archive',str(archive)],check=True)
            dest=work/archive.stem;dest.mkdir()
            if archive.name.endswith('.tar.gz'):
                with tarfile.open(archive) as tar:tar.extractall(dest,filter='data')
            else:
                with zipfile.ZipFile(archive) as z:z.extractall(dest)
            subprocess.run([str(scanner),'dir',str(dest),'--redact=100','--no-banner'],check=True)

if __name__=='__main__':main()
