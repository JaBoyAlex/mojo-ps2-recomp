"""Cross-platform builder contracts, without game fixtures."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('native_builder',ROOT/'builder/build.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class NativeTests(unittest.TestCase):
    def test_linux_clock_patch_is_repeatable_and_platform_limited(self):
        spec=importlib.util.spec_from_file_location('platform_patch',ROOT/'builder/platform_support.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            engine=Path(temporary)
            (engine/'scripts').mkdir();(engine/'host').mkdir()
            for name in ('setup.sh','port.sh','cxx.sh'):
                (engine/'scripts'/name).write_text('')
            window=engine/'host/window.cpp'
            original='#include "window.hpp"\nauto ticks = SDL_GetPerformanceCounter();\nauto hz = SDL_GetPerformanceFrequency();\n'
            window.write_text(original)
            with patch.object(module.sys,'platform','darwin'):
                module.apply(engine)
                self.assertEqual(window.read_text(),original)
            with patch.object(module.sys,'platform','linux'):
                module.apply(engine);first=window.read_text();module.apply(engine)
                self.assertEqual(window.read_text(),first)
                self.assertEqual(first.count('#include "mojo_host_clock.hpp"'),1)
                self.assertIn('mojo::host_clock::counter()',first)
                self.assertIn('mojo::host_clock::frequency()',first)
                self.assertNotIn('SDL_GetPerformance',first)

    def test_versioned_distribution_clang_is_accepted(self):
        sys.path.insert(0,str(ROOT/'builder'))
        try:
            spec=importlib.util.spec_from_file_location('bootstrap_native_test',ROOT/'builder/bootstrap_native.py')
            bootstrap=importlib.util.module_from_spec(spec);spec.loader.exec_module(bootstrap)
        finally:
            sys.path.pop(0)
        with patch.dict(os.environ,{},clear=True), patch.object(bootstrap.shutil,'which',side_effect=lambda name:'/tools/clang++-19' if name=='clang++-19' else None):
            self.assertEqual(bootstrap.native_compiler(),'/tools/clang++-19')
            self.assertEqual(os.environ['CXX'],'/tools/clang++-19')

    def test_unicode_paths_and_lock_released(self):
        with tempfile.TemporaryDirectory(prefix='MOJO é spaces ') as temp:
            path=Path(temp)/'exclusive.lock'
            with builder.acquire_lock(path):
                code='import sys;sys.path.insert(0,sys.argv[1]);import build;build.acquire_lock(sys.argv[2])'
                result=subprocess.run([sys.executable,'-c',code,str(ROOT/'builder'),str(path)],capture_output=True)
                self.assertNotEqual(result.returncode,0)
            builder.acquire_lock(path).close()

    def test_process_group_timeout(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(builder.Failure) as caught:
                builder.run([sys.executable,'-c','import time;time.sleep(60)'],temp,Path(temp)/'private.log',timeout=.1)
            self.assertEqual(caught.exception.code,23)

    def test_platform_architecture_separates_cache(self):
        self.assertIn('-',builder.host_id())
        self.assertEqual(builder.executable('runtime'),'runtime.exe' if os.name=='nt' else 'runtime')

    def test_disc_hashes_are_unchanged(self):
        self.assertEqual(builder.SERIAL,'SLUS_207.41')
        self.assertEqual(builder.ISO_SHA256,'bcfba449a662cc898868317c4bc415e9a2084a53ae8b92b7a4a19efbaa54f3c5')
        self.assertEqual(builder.ELF_SHA256,'b749b3765aa3c74d594ec502686246965b69e8492c49ac08f5283a245adc8a60')

if __name__=='__main__':unittest.main()
