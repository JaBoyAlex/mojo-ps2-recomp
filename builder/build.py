"""One local pipeline for standalone and RecompLauncher. No game bytes are shipped."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

VERSION = '1.0.0-rc.7'
PIPELINE = '57ef1197-2d-upscale-4'
ISO_SHA256 = 'bcfba449a662cc898868317c4bc415e9a2084a53ae8b92b7a4a19efbaa54f3c5'
ELF_SHA256 = 'b749b3765aa3c74d594ec502686246965b69e8492c49ac08f5283a245adc8a60'
SERIAL = 'SLUS_207.41'

class Failure(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message

def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def progress(value, message):
    print(f'progress {value:.2f} {message}', flush=True)

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.new')
    temp.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temp.replace(path)

def run(command, cwd, log, timeout=3600, failure_code=22):
    with open(log, 'ab') as out:
        try:
            result = subprocess.Popen([str(v) for v in command], cwd=cwd, stdout=out, stderr=subprocess.STDOUT)
            result.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill', '/PID', str(result.pid), '/T', '/F'], stdout=out, stderr=out)
            raise Failure(23, 'Build timed out. Keep the private logs locally and retry setup.')
    if result.returncode:
        if failure_code == 20:
            raise Failure(20, 'Invalid or unsupported disc image. Supply the verified USA PS2 ISO, BIN/CUE or single-track CHD.')
        raise Failure(22, 'A build tool failed. See userdata/cache private logs; do not upload them unredacted.')

def validate(iso, engine, scratch):
    # Import the exact same importer the upstream build uses; inspect only after full-image hash validation.
    if digest(iso) != ISO_SHA256:
        raise Failure(20, 'Unsupported or damaged disc. Required: MOJO! USA, SLUS_207.41, SYSTEM.CNF VER 1.02, exact hash in docs/COMPATIBILITY.md. Other regions/revisions are not supported.')
    run([sys.executable, '-I', engine/'scripts/disc.py', 'extract', iso, scratch, SERIAL], engine, scratch/'validate-private.log')
    if digest(scratch/SERIAL) != ELF_SHA256:
        raise Failure(20, 'Boot executable checksum mismatch.')

def prepare(args, state):
    engine = args.engine
    cache = state/'cache'
    cache.mkdir(parents=True, exist_ok=True)
    active_path = state/'active.json'
    source = args.game
    active = json.loads(active_path.read_text()) if active_path.exists() else {}
    if not isinstance(active, dict): raise Failure(21, 'Invalid local build index. Restore userdata/active.json from a backup.')
    if source is None:
        source = state/'disc.iso'
    if not source.is_file():
        raise Failure(20, 'Select your own MOJO! USA PS2 ISO, BIN/CUE, or single-track CD CHD. No game is included.')
    progress(.08, 'Validating your disc image')
    candidate = cache/'import.iso'
    if source.suffix.lower() == '.iso':
        iso = source
    elif source.suffix.lower() in ('.bin', '.cue', '.img'):
        run([sys.executable, '-I', engine/'scripts/disc.py', 'iso', source, candidate], engine, cache/'import-private.log', failure_code=20)
        iso = candidate
    elif source.suffix.lower() == '.chd':
        converter = args.root/'chd_to_iso.exe'
        if not converter.is_file():
            raise Failure(21, 'CHD reader is missing. Use the portable release or convert your own disc to ISO first.')
        run([converter, source, candidate], engine, cache/'import-private.log', failure_code=20)
        iso = candidate
    else:
        raise Failure(20, 'Unsupported image container. Use ISO, BIN/CUE, or single-track CD CHD.')
    validate(iso, engine, cache)
    import importlib.util
    for name in ('display_labels', 'camera_controls', 'hud_upscale'):
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
        patch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(patch)
        patch.apply(engine)
    disc = state/'disc.iso'
    if iso.resolve() != disc.resolve():
        shutil.copyfile(iso, disc.with_suffix('.new'))
        disc.with_suffix('.new').replace(disc)
    game = engine/'games/mojo'
    game.mkdir(parents=True, exist_ok=True)
    engine_disc = game/'disc.iso'
    if not engine_disc.exists() or digest(engine_disc) != ISO_SHA256:
        shutil.copyfile(disc, engine_disc)
    if active.get('version') == VERSION and active.get('pipeline') == PIPELINE:
        dest = state/'builds'/active.get('build', '')
        if (dest/'runtime.exe').is_file() and digest(dest/'runtime.exe') == active.get('runtime_sha256'):
            progress(1, 'Verified local build is ready')
            return dest
    progress(.20, 'Compiling the open-source runtime and translating your local game (several minutes)')
    run([shutil.which('bash.exe'), 'scripts/port.sh', 'mojo', disc, '--native-only'], engine, cache/'build-private.log')
    progress(.90, 'Installing the local build without replacing saves')
    dest = state/'builds'/(VERSION+'-'+uuid.uuid4().hex[:8])
    dest.mkdir(parents=True)
    native = engine/'build/native-mojo'
    shutil.copy2(native/'ps2run.exe', dest/'runtime.exe')
    for dll in native.glob('*.dll'):
        shutil.copy2(dll, dest/dll.name)
    # Keep the exact portable compiler on PATH for previously unseen EE/VU blocks.
    saves = state/'saves'
    saves.mkdir(exist_ok=True)
    card = saves/'mojo.ps2'
    if not card.exists():
        run([sys.executable, '-I', engine/'scripts/mcformat.py', card], engine, cache/'card-private.log')
    write_json(active_path, {'version': VERSION, 'pipeline': PIPELINE, 'build': dest.name, 'runtime_sha256': digest(dest/'runtime.exe')})
    progress(1, 'Your native MOJO! build is ready')
    return dest

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--engine', type=Path, required=True)
    p.add_argument('--game', type=Path)
    p.add_argument('--prepare', action='store_true')
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--fullscreen', action='store_true')
    args = p.parse_args()
    args.root = args.root.resolve()
    args.engine = args.engine.resolve()
    if args.game: args.game = args.game.resolve()
    state = args.root/'userdata'
    state.mkdir(parents=True, exist_ok=True)
    # Windows exclusive file locking is released even after a crash.
    import msvcrt
    lock = open(state/'builder.lock', 'a+b')
    lock.seek(0)
    try:
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print('Another builder or game is using this installation. Close it first.')
        return 24
    try:
        dest = prepare(args, state)
        if args.prepare: return 0
        os.environ['PS2_WINDOW_TITLE'] = 'MOJO! Native PC'
        settings_path = state/'settings.json'
        settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        if not isinstance(settings, dict): raise Failure(21, 'Invalid settings file. Restore userdata/settings.json from a backup.')
        if not settings_path.exists(): write_json(settings_path, {'fullscreen': False})
        scale = settings.get('render_scale')
        if str(scale) in ('1','2','3','4'): os.environ['PS2_SCALE'] = str(scale)
        command = [dest/'runtime.exe', '--disc', state/'disc.iso', '--game-dir', state/'saves', '--memcard', state/'saves/mojo.ps2']
        if args.smoke:
            command += ['--frames', '3100', '--press', '300:start', '--press', '600:cross']
        else:
            command += ['--fullscreen' if args.fullscreen or str(settings.get('fullscreen')).lower() == 'true' or os.getenv('RECOMPLAUNCHER_MODE') == 'bigpicture' else '--window']
        with open(state/'cache/runtime-private.log', 'wb') as log:
            result = subprocess.run([str(v) for v in command], cwd=dest, stdout=log, stderr=log)
        if result.returncode: print('The native runtime stopped with an error. Private details remain in userdata/cache/runtime-private.log.')
        return result.returncode
    except Failure as error:
        print(error.message, flush=True)
        return error.code
    except (OSError, ValueError, KeyError):
        print('Local setup is incomplete or inaccessible. Check disk space and write permission, then retry.')
        return 21
    finally:
        lock.close()

if __name__ == '__main__':
    sys.exit(main())
