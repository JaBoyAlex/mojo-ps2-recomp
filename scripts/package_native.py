"""Package native Unix helpers only; never package a generated game runtime."""
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import shutil
import subprocess
import sys
import zipfile
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'builder'))
import bootstrap_native as bootstrap
import build

def manifest(system):
    value = json.loads((ROOT/'recomplauncher.json').read_text())
    entry = 'MOJO.app/Contents/MacOS/MOJO' if system == 'macos' else 'MOJO'
    for action in ('prepare', 'start'): value[action]['program'] = [entry]
    value['game']['label'] = value['game']['label'].split('First setup')[0] + (
        'First setup downloads verified native build tools and needs several GB free. '
        + ('Requires Apple Command Line Tools; see docs/PLATFORMS.md.' if system == 'macos'
           else 'Requires a native Clang toolchain and Linux development prerequisites; see docs/PLATFORMS.md.'))
    if system == 'macos':
        # App bundles may be read-only or translocated. Data stays outside the bundle.
        encoded = json.dumps(value).replace('{install}/userdata', '{home}/Library/Application Support/MOJO Recomp')
        value = json.loads(encoded)
    return value

def main():
    system = 'macos' if sys.platform == 'darwin' else 'linux'
    arch = 'arm64' if platform.machine().lower() in ('arm64','aarch64') else 'x64'
    out = ROOT/'build/native-helpers'
    cache = ROOT/'build/native-dependencies'
    cache.mkdir(parents=True, exist_ok=True)
    chd = next(p for p in bootstrap.unpack('libchdr', cache).iterdir() if p.is_dir())
    compiler = bootstrap.native_compiler()
    c_compiler = os.environ.get('CC',compiler.replace('clang++','clang'))
    subprocess.run(['cmake','-S',str(ROOT),'-B',str(out),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release',
                    '-DCMAKE_C_COMPILER='+c_compiler,'-DCMAKE_CXX_COMPILER='+compiler,'-DLIBCHDR_SOURCE='+str(chd)], check=True)
    subprocess.run(['cmake','--build',str(out),'-j','4'],check=True)
    stage = ROOT/'build/native-package'/f'{system}-{arch}'
    stage.mkdir(parents=True, exist_ok=True)
    source_names = json.loads((ROOT/'publication-files.json').read_text())
    resources = stage/'MOJO.app/Contents/Resources' if system == 'macos' else stage
    for name in source_names:
        dest = resources/name; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name,dest)
    for name in ('MOJO','chd_to_iso'):
        dest = stage/'MOJO.app/Contents/MacOS/MOJO' if system == 'macos' and name == 'MOJO' else resources/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(out/name,dest); dest.chmod(0o755)
    if system == 'macos':
        info=plistlib.loads((ROOT/'src/Info.plist').read_bytes())
        info['CFBundleShortVersionString']=build.VERSION.split('-')[0]
        info['CFBundleVersion']=build.VERSION.split('-')[0]
        (stage/'MOJO.app/Contents/Info.plist').write_bytes(plistlib.dumps(info))
        # Ad-hoc integrity signing permits local execution; this is NOT Developer ID signing or notarization.
        subprocess.run(['codesign','--force','--sign','-',str(resources/'chd_to_iso')],check=True)
        subprocess.run(['codesign','--force','--sign','-',str(stage/'MOJO.app')],check=True)
        subprocess.run(['codesign','--verify','--strict',str(stage/'MOJO.app')],check=True)
    else:
        (stage/'Start-MOJO.sh').chmod(0o755)
    (stage/'recomplauncher.json').write_text(json.dumps(manifest(system),indent=2)+'\n')
    subprocess.run([sys.executable,str(ROOT/'scripts/check_manifest.py'),str(stage/'recomplauncher.json')],check=True)
    dist = ROOT/'dist'; dist.mkdir(exist_ok=True)
    # Version stays separate from the stable release until real platform gameplay is verified.
    extension='.zip' if system=='macos' else '.tar.gz'
    label='macOS' if system=='macos' else 'Linux'
    archive = dist/f'MOJO-Recomp-v{build.VERSION}-{label}-{arch}{extension}'
    if system=='macos':
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for path in sorted(stage.rglob('*')):
                if path.is_file(): z.write(path,path.relative_to(stage).as_posix())
    else:
        def public_metadata(entry):
            entry.uid=entry.gid=0
            entry.uname=entry.gname=''
            entry.mtime=0
            return entry
        with tarfile.open(archive,'w:gz') as tar:
            for path in sorted(stage.rglob('*')):
                if path.is_file(): tar.add(path,arcname=path.relative_to(stage).as_posix(),recursive=False,filter=public_metadata)
    subprocess.run([sys.executable,str(ROOT/'scripts/verify_publication.py'),'--archive',str(archive)],check=True)
    Path(str(archive)+'.sha256').write_text(build.digest(archive)+'  '+archive.name+'\n')
    executable = stage/'MOJO.app/Contents/MacOS/MOJO' if system == 'macos' else stage/'MOJO'
    subprocess.run([str(executable),'--self-test'],check=True)
    print('Packaged audited native helpers for '+system+' '+arch)

if __name__ == '__main__': main()
