"""Exercise the exact production fast-clear guard and parameter builder."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import tempfile

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine', required=True, type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('fast_clear', root/'builder/fast_clear.py')
    patch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patch)
    patch.apply(args.engine.resolve())
    patch.apply(args.engine.resolve())
    with tempfile.TemporaryDirectory() as temp:
        exe = Path(temp)/'clear-test.exe'
        subprocess.run(['clang++','-O2','-std=c++20','-static','-I'+str(root/'builder'),
                        str(root/'tests/fast_clear.cpp'),'-o',str(exe)],check=True,timeout=120)
        subprocess.run([str(exe)],check=True,timeout=30)

if __name__ == '__main__':
    main()
