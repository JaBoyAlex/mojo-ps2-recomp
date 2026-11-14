"""Compile the actual upstream queue with synthetic packet-ordering tests."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    args = parser.parse_args()
    engine = args.engine.resolve()
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('queue_offsets', root/'builder/queue_offsets.py')
    patch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patch)
    patch.apply(engine)
    patch.apply(engine)
    with tempfile.TemporaryDirectory() as folder:
        exe = Path(folder)/'queue-test.exe'
        subprocess.run(['clang++', '-O2', '-std=c++20', '-static',
                        '-I'+str(engine/'runtime/src'), '-I'+str(engine/'runtime/include'),
                        str(root/'tests/queue_offsets.cpp'), str(engine/'runtime/src/gs/queue.cpp'),
                        '-lsynchronization', '-o', str(exe)], check=True, timeout=120)
        subprocess.run([str(exe)], check=True, timeout=120)


if __name__ == '__main__':
    main()
