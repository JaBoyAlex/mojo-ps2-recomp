"""Native-host validation using synthetic code only. No MOJO! data enters CI."""
import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'builder'))
import bootstrap_native as bootstrap

def run(*command, cwd=None, env=None):
    subprocess.run([str(v) for v in command],cwd=cwd,env=env,check=True,timeout=1200)

def main():
    with tempfile.TemporaryDirectory(prefix='MOJO native spaces é ') as temporary:
        work=Path(temporary)
        engine=bootstrap.configure(ROOT,work)
        for name in ('display_labels','camera_controls','hud_upscale','queue_offsets','fast_clear','platform_support'):
            spec=importlib.util.spec_from_file_location(name,ROOT/'builder'/(name+'.py'))
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.apply(engine);module.apply(engine)
        run('bash','scripts/setup.sh','--native-only',cwd=engine)
        tools=engine/'build/tools'
        run(sys.executable,engine/'scripts/test_live_image.py',tools/'eerecomp')
        # Independently authored MIPS loop in a minimal ELF. It contains no commercial bytes.
        elf=bytearray(0x110)
        elf[:16]=bytes([127,69,76,70,1,1,1])+bytes(9)
        struct.pack_into('<HHIIIIIHHHHHH',elf,16,2,8,1,0x100000,52,0,0,52,32,1,0,0,0)
        struct.pack_into('<IIIIIIII',elf,52,1,0x100,0x100000,0x100000,16,16,5,16)
        struct.pack_into('<IIII',elf,0x100,0x1000ffff,0,0,0)
        fixture=work/'synthetic.elf';fixture.write_bytes(elf)
        generated=work/'generated'
        run(tools/'eerecomp',fixture,'--out',generated)
        native=work/'native'
        compiler=os.environ.get('CXX','clang++')
        run('cmake','-S',engine,'-B',native,'-G','Ninja','-DCMAKE_BUILD_TYPE=Release',
            '-DCMAKE_CXX_COMPILER='+compiler,'-DCMAKE_CXX_FLAGS=-ffp-contract=off','-DPS2_GENERATED='+str(generated))
        targets=['ps2run','ps2padtest','ps2savetest','ps2discinputtest','ps2vuregtest','ps2bigstacktest']
        run('cmake','--build',native,'-j','3','--target',*targets)
        for target in targets[2:]:run(native/target)
        env=os.environ.copy();env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='dummy'
        run(native/'ps2padtest',env=env)
        run(native/'ps2run',fixture,'--frames','3',env=env)
        # Build production controls and portable queue guards through a small CMake harness.
        harness=work/'guards';harness.mkdir()
        (harness/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(native_guards CXX)
set(CMAKE_CXX_STANDARD 20)
find_package(SDL2 REQUIRED)
add_executable(camera "${PROJECT_SOURCE}/tests/camera_controls.cpp" "${ENGINE}/host/keymap.cpp" "${ENGINE}/host/quickmenu.cpp")
target_include_directories(camera PRIVATE "${ENGINE}/host")
target_compile_definitions(camera PRIVATE SDL_MAIN_HANDLED)
target_link_libraries(camera PRIVATE SDL2::SDL2)
add_executable(clear "${PROJECT_SOURCE}/tests/fast_clear.cpp")
target_include_directories(clear PRIVATE "${PROJECT_SOURCE}/builder")
add_executable(queue "${PROJECT_SOURCE}/tests/queue_offsets.cpp" "${ENGINE}/runtime/src/gs/queue.cpp")
target_include_directories(queue PRIVATE "${ENGINE}/runtime/src" "${ENGINE}/runtime/include")
target_link_libraries(queue PRIVATE pthread)
add_executable(live "${ENGINE}/tests/live_link.cpp" "${ENGINE}/runtime/src/live_build.cpp")
target_include_directories(live PRIVATE "${ENGINE}/runtime/include" "${ENGINE}/runtime/src")
target_link_libraries(live PRIVATE ${CMAKE_DL_LIBS})
''')
        # Upstream's synthetic fixture predates hidden-visibility live libraries. Export only its test symbols.
        link=engine/'tests/live_link.cpp'
        text=link.read_text().replace('extern \\"C\\" int ps2_live_link_test_', 'extern \\"C\\" __attribute__((visibility(\\"default\\"))) int ps2_live_link_test_')
        link.write_text(text)
        run('cmake','-S',harness,'-B',harness/'out','-G','Ninja','-DCMAKE_CXX_COMPILER='+compiler,
            '-DPROJECT_SOURCE='+str(ROOT),'-DENGINE='+str(engine))
        run('cmake','--build',harness/'out','-j','3')
        for target in ('camera','clear','queue','live'):run(harness/'out'/target,work)
        run('cmake','--build',native,'-j','3','--target','ps2run')
        print('PASS: synthetic generation, native startup, saves, virtual pad, VU, queue, clear, live library load and no-op rebuild')

if __name__=='__main__':main()
