"""Compile and exercise actual patched host controls without any game files."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import subprocess

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',required=True,type=Path)
    p.add_argument('--sdl2',type=Path,help='Verified SDL2 development directory prepared by packaging')
    args=p.parse_args()
    engine=args.engine.resolve()
    root=Path(__file__).resolve().parents[1]
    for name in ('display_labels','camera_controls','hud_upscale'):
        spec=importlib.util.spec_from_file_location(name,root/'builder'/(name+'.py'))
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        module.apply(engine)
        module.apply(engine)
    sdl=args.sdl2.resolve() if args.sdl2 else engine/'third_party/sdl2'
    if not (sdl/'lib/libSDL2.dll.a').exists():
        if args.sdl2:
            p.error('SDL2 development files are missing; run scripts/package.ps1 to fetch the pinned package.')
        subprocess.run([shutil.which('bash.exe'),'scripts/fetch_sdl2.sh'],cwd=engine,check=True)
    build=root/'build/camera-tests'; build.mkdir(parents=True,exist_ok=True)
    exe=build/'camera-controls-test.exe'
    subprocess.run(['clang++','-std=c++20','-O2','-static','-DSDL_MAIN_HANDLED',
                    str(root/'tests/camera_controls.cpp'),str(engine/'host/keymap.cpp'),
                    str(engine/'host/quickmenu.cpp'),'-I'+str(engine/'host'),
                    '-I'+str(sdl/'include/SDL2'),str(sdl/'lib/libSDL2.dll.a'),'-o',str(exe)],check=True)
    shutil.copy2(sdl/'bin/SDL2.dll',build/'SDL2.dll')
    subprocess.run([str(exe)],check=True)
    print('PASS: independent camera controls, HUD setting persistence and F1 menu selection')

if __name__=='__main__': main()
