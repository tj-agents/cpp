import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GENERATOR=ROOT/'.agents/gen_skill_routes.py'
class RouteCliTests(unittest.TestCase):
 def test_canonical_profiles(self):
  for toolchain in (None,'gpp','msvc'):
   with tempfile.TemporaryDirectory() as temporary:
    command=[sys.executable,str(GENERATOR),'--into',temporary]
    if toolchain: command.extend(['--toolchain',toolchain])
    result=subprocess.run(command,capture_output=True,text=True)
    self.assertEqual(0,result.returncode,result.stdout+result.stderr)
    payload=json.loads((Path(temporary)/'.agents/skill-routes.json').read_text())
    self.assertEqual(toolchain,payload['profile']['toolchain'])
 def test_retired_arguments_rejected(self):
  result=subprocess.run([sys.executable,str(GENERATOR),'--kind','gcc','--into',str(ROOT)],capture_output=True,text=True)
  self.assertNotEqual(0,result.returncode)
if __name__=='__main__': unittest.main()
