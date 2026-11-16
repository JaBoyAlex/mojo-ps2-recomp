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

def synthetic_iso(elf):
    image=bytearray(64*2048)
    def record(name,lba,size,directory=False):
        name=name if isinstance(name,bytes) else name.encode('ascii')
        row=bytearray(33+len(name)+(len(name)%2==0))
        row[0]=len(row);struct.pack_into('<I',row,2,lba);struct.pack_into('>I',row,6,lba)
        struct.pack_into('<I',row,10,size);struct.pack_into('>I',row,14,size)
        row[25]=2 if directory else 0;row[28:32]=b'\x01\x00\x00\x01';row[32]=len(name);row[33:33+len(name)]=name
        return row
    image[16*2048:16*2048+7]=b'\x01CD001\x01'
    struct.pack_into('<I',image,16*2048+80,64);struct.pack_into('>I',image,16*2048+84,64)
    image[16*2048+156:16*2048+190]=record(b'\0',20,2048,True)
    image[17*2048:17*2048+7]=b'\xffCD001\x01'
    cnf=b'BOOT2 = cdrom0:\\SYNTH.ELF;1\nVER = 1.00\n'
    directory=record(b'\0',20,2048,True)+record(b'\1',20,2048,True)+record('SYSTEM.CNF;1',21,len(cnf))+record('SYNTH.ELF;1',22,len(elf))
    image[20*2048:20*2048+len(directory)]=directory
    image[21*2048:21*2048+len(cnf)]=cnf;image[22*2048:22*2048+len(elf)]=elf
    return image

def main():
    with tempfile.TemporaryDirectory(prefix='MOJO native spaces é ') as temporary:
        work=Path(temporary)
        engine=bootstrap.configure(ROOT,work)
        for name in ('display_labels','camera_controls','hud_upscale','queue_offsets','fast_clear','platform_support'):
            spec=importlib.util.spec_from_file_location(name,ROOT/'builder'/(name+'.py'))
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.apply(engine);module.apply(engine)
        # The pinned pad fixture predates frame-latched input and the Guide menu.
        # Advance the real latch in this synthetic test (no game loop is running).
        # This test-only hook is never added by the player's bootstrap/patches.
        system=engine/'runtime/src/system.cpp'
        system.write_text(system.read_text()+'\nnamespace ps2 { void native_test_latch_pads() { latch_pads(); } }\n')
        pad=engine/'host/pad_test.cpp';text=pad.read_text()
        text=text.replace('    poll_input();\n}', '''    poll_input();
    if (b == SDL_CONTROLLER_BUTTON_BACK) { SDL_Delay(down ? 310 : 90); poll_input(); }
}''',1)
        text=text.replace('poll_input();','frame_input();')
        text=text.replace('namespace {','namespace ps2 { void native_test_latch_pads(); }\nstatic void frame_input() { poll_input(); ps2::native_test_latch_pads(); }\n\nnamespace {',1)
        text=text.replace('    button(0, SDL_CONTROLLER_BUTTON_GUIDE, false);', '''    button(0, SDL_CONTROLLER_BUTTON_GUIDE, false);
    button(0, SDL_CONTROLLER_BUTTON_GUIDE, true);  // close the real Guide menu
    button(0, SDL_CONTROLLER_BUTTON_GUIDE, false);''',1)
        pad.write_text(text)
        # Independently authored MIPS loop in a minimal ELF. It contains no commercial bytes.
        elf=bytearray(0x110)
        elf[:16]=bytes([127,69,76,70,1,1,1])+bytes(9)
        struct.pack_into('<HHIIIIIHHHHHH',elf,16,2,8,1,0x100000,52,0,0,52,32,1,0,0,0)
        struct.pack_into('<IIIIIIII',elf,52,1,0x100,0x100000,0x100000,16,16,5,16)
        struct.pack_into('<IIII',elf,0x100,0x1000ffff,0,0,0)
        fixture=work/'synthetic.elf';fixture.write_bytes(elf)
        disc=work/'synthetic disc.iso';disc.write_bytes(synthetic_iso(elf))
        run('bash','scripts/port.sh','ci-synthetic',disc,'--native-only','--no-explore',cwd=engine)
        tools=engine/'build/tools'
        run(sys.executable,engine/'scripts/test_live_image.py',tools/'eerecomp')
        generated=engine/'generated/ci-synthetic'
        native=engine/'build/native-ci-synthetic'
        compiler=os.environ.get('CXX','clang++')
        run('cmake','-S',engine,'-B',native,'-G','Ninja','-DCMAKE_BUILD_TYPE=Release',
            '-DCMAKE_CXX_COMPILER='+compiler,'-DPS2_GENERATED='+str(generated))
        # The upstream ps2vuregtest CMake target links stubbed globals to the full
        # runtime (duplicate symbols); use its standalone code-generation suites.
        targets=['ps2run','ps2padtest','ps2savetest','ps2discinputtest','ps2bigstacktest']
        run('cmake','--build',native,'-j','3','--target',*targets)
        for target in targets[2:]:run(native/target)
        env=os.environ.copy();env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='dummy'
        run(native/'ps2padtest',env=env)
        run(native/'ps2run',fixture,'--frames','3',env=env)
        run(sys.executable,engine/'scripts/test_vu0_codegen.py')
        run(sys.executable,engine/'scripts/test_vu_codegen.py',compiler)
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
