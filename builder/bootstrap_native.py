"""Native Unix bootstrap. Disc import, validation, compilation and play remain in build.py."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile

import build
import platform_support

def fetch(name, cache):
    record = json.loads(Path(__file__).with_name('native-dependencies.json').read_text())[name]
    path = cache/(name + '.zip')
    if not path.exists() or build.digest(path) != record['sha256']:
        temporary = path.with_suffix('.download')
        request = urllib.request.Request(record['url'], headers={'User-Agent': 'MOJO-Recomp-builder'})
        with urllib.request.urlopen(request, timeout=60) as source, temporary.open('wb') as dest:
            shutil.copyfileobj(source, dest)
        if build.digest(temporary) != record['sha256']:
            temporary.unlink()
            raise build.Failure(21, 'Dependency checksum mismatch; setup stopped safely.')
        temporary.replace(path)
    return path

def unpack(name, cache):
    record = json.loads(Path(__file__).with_name('native-dependencies.json').read_text())[name]
    dest = cache/(name+'-'+record['sha256'][:12])
    if not (dest/'.complete').exists():
        archive = fetch(name, cache)
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as source:
            for entry in source.infolist():
                target = dest/entry.filename
                if not target.resolve().is_relative_to(dest.resolve()):
                    raise build.Failure(21, 'Unsafe dependency archive path.')
                source.extract(entry, dest)
                if entry.external_attr >> 16 & 0o111 and target.is_file():
                    target.chmod(target.stat().st_mode | 0o111)
        (dest/'.complete').touch()
    return dest

def configure(root, state):
    os.environ['PATH'] = str(Path(sys.executable).parent)+os.pathsep+os.environ.get('PATH', '')
    system = 'macos' if sys.platform == 'darwin' else 'linux'
    if system == 'linux' and platform.machine().lower() not in ('x86_64', 'amd64'):
        raise build.Failure(21, 'This package supports Linux x86-64 only.')
    cache = state/'cache'/('native-tools-'+build.host_id())
    cache.mkdir(parents=True, exist_ok=True)
    # One lock also protects extraction and dependency builds, before build.py takes over.
    with build.acquire_lock(state/'bootstrap.lock'):
        build.progress(.01, 'Preparing verified native build tools')
        for name in ('cmake', 'ninja'):
            package = unpack(name+'-'+system, cache)
            binary = package/name/'data/bin' if name == 'cmake' else package/'ninja-1.11.1.4.data/scripts'
            for tool in binary.iterdir():
                if tool.is_file(): tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
            os.environ['PATH'] = str(binary)+os.pathsep+os.environ.get('PATH', '')
        if not shutil.which('clang++'):
            raise build.Failure(21, 'Install a native Clang C++20 toolchain: Apple Command Line Tools on macOS; clang-19, libc++-19-dev and libc++abi-19-dev on Debian/Ubuntu. See docs/PLATFORMS.md.')
        engine = next(p for p in unpack('engine', cache).iterdir() if p.is_dir())
        platform_support.apply(engine)
        jobs = str(max(1, min(6, (os.cpu_count() or 2)-2)))
        os.environ.setdefault('PS2_JOBS', jobs)
        sdl = cache/'sdl2-install'
        if not (sdl/'lib/cmake/SDL2/SDL2Config.cmake').exists():
            source = next(p for p in unpack('sdl2', cache).iterdir() if p.is_dir())
            out = cache/'sdl2-build'
            build.run(['cmake', '-S', source, '-B', out, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
                       '-DCMAKE_INSTALL_PREFIX='+str(sdl), '-DSDL_SHARED=OFF', '-DSDL_STATIC=ON',
                       '-DSDL_TEST=OFF'], root, cache/'sdl2-private.log')
            build.run(['cmake', '--build', out, '--target', 'install', '-j', jobs], root, cache/'sdl2-private.log')
        os.environ['CMAKE_PREFIX_PATH'] = str(sdl)+os.pathsep+os.environ.get('CMAKE_PREFIX_PATH', '')
        return engine

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--game', type=Path)
    args, rest = parser.parse_known_args()
    root = args.root.resolve()
    state = Path.home()/'Library/Application Support/MOJO Recomp' if sys.platform == 'darwin' else root/'userdata'
    try:
        state.mkdir(parents=True, exist_ok=True)
        # Reject incorrect ISO files before downloading/building other tools.
        # Correct images still undergo the original full-image + ELF verification.
        if args.game:
            args.game = args.game.resolve()
            if not args.game.is_file(): raise build.Failure(20, 'The selected disc image is missing or inaccessible.')
            if args.game.suffix.lower() == '.iso' and build.digest(args.game) != build.ISO_SHA256:
                raise build.Failure(20, 'Unsupported or damaged disc. Required: MOJO! USA SLUS_207.41, SYSTEM.CNF VER 1.02; see docs/COMPATIBILITY.md.')
            rest += ['--game', str(args.game)]
        elif '--prepare' in rest and not (state/'disc.iso').exists():
            raise build.Failure(20, 'Headless setup requires --game with your supported MOJO! disc image.')
        with build.acquire_lock(state/'session.lock'):
            engine = configure(root, state)
            sys.argv = [str(root/'builder/build.py'), '--root', str(root), '--state', str(state), '--engine', str(engine), *rest]
            return build.main()
    except build.Failure as error:
        print(error.message, flush=True)
        return error.code
    except BlockingIOError:
        print('Another setup is running. Close it first.', flush=True)
        return 24
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print('Native tools could not be prepared. Check internet access, disk space and native toolchain prerequisites.', flush=True)
        return 21

if __name__ == '__main__': sys.exit(main())
