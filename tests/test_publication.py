import importlib.util
from pathlib import Path
import unittest

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gate',root/'scripts/verify_publication.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)

class PublicationTests(unittest.TestCase):
    def test_renamed_executable_is_blocked(self):
        self.assertIn(('README.md','game-data'),gate.check('README.md',bytes([127])+b'ELF'+bytes([1,1,1])))

    def test_generated_code_path_is_blocked(self):
        self.assertIn(('generated/mojo/unit.cpp','not-allowlisted'),gate.check('generated/mojo/unit.cpp',b'synthetic'))

    def test_private_path_is_blocked_even_in_binary(self):
        sample=b'C:'+bytes([92])+b'Users'+bytes([92])+b'example-person'+bytes([92])+b'private'
        self.assertIn(('MOJO.exe','private-home-path'),gate.check('MOJO.exe',b'MZ'+sample,True))
        self.assertIn(('MOJO.exe','private-home-path'),gate.check('MOJO.exe',b'MZ'+sample.decode().encode('utf-16-le'),True))

    def test_release_does_not_allow_game_executable(self):
        self.assertIn(('runtime.exe','not-allowlisted'),gate.check('runtime.exe',b'MZ',True))

if __name__=='__main__': unittest.main()
