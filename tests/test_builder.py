"""Synthetic tests only. Never upload a commercial game fixture."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',root/'builder/build.py')
builder=importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)

class BuilderTests(unittest.TestCase):
    def test_wrong_disc_fails_before_tools(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'fake.iso'; p.write_bytes(b'synthetic invalid disc')
            with self.assertRaises(builder.Failure) as result: builder.validate(p,Path('nonexistent'),Path(temp))
            self.assertEqual(result.exception.code,20)

    def test_atomic_settings_preserve_neighbors(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); save=root/'save'; save.write_bytes(b'player-owned sentinel')
            builder.write_json(root/'settings.json',{'fullscreen':True})
            builder.write_json(root/'settings.json',{'fullscreen':False})
            self.assertEqual(save.read_bytes(),b'player-owned sentinel')
            self.assertEqual(json.loads((root/'settings.json').read_text()),{'fullscreen':False})
            self.assertFalse((root/'settings.new').exists())

    def test_manifest_uses_same_entrypoint(self):
        m=json.loads((root/'recomplauncher.json').read_text(encoding='utf-8'))
        self.assertEqual(m['prepare']['program'],m['start']['program'])
        self.assertIn('--prepare',m['prepare']['args'])
        self.assertGreaterEqual(m['prepare']['timeout'],3600)
        self.assertNotIn('userdata/',json.loads((root/'publication-files.json').read_text()))

if __name__=='__main__': unittest.main()
