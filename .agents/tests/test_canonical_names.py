import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class CanonicalNameTests(unittest.TestCase):
    def test_only_canonical_packages_and_skills_are_published(self):
        payloads=json.loads((ROOT/'.agents/plugins/payloads.json').read_text(encoding='utf-8'))
        sources=json.loads((ROOT/'.agents/plugins/sources.json').read_text(encoding='utf-8'))
        self.assertEqual(['cpp','gpp','msvc','win32'], payloads['publicPlugins'])
        self.assertEqual(set(payloads['publicPlugins']), set(payloads['payloads']))
        self.assertNotIn('compatibilityAliases', payloads)
        for scope in sources['scopes']:
            plugin=scope['plugin']
            authored={p.parent.name for p in (ROOT/scope['root']).glob('*/*/SKILL.md')}
            shipped={p.parent.name for p in (ROOT/'plugins'/plugin/'skills').glob('*/SKILL.md')}
            self.assertEqual(authored, shipped)

    def test_host_adapters_resolve_canonical_sources(self):
        sources=json.loads((ROOT/'.agents/plugins/sources.json').read_text(encoding='utf-8'))
        for adapter_root in sources['host_adapter_roots'].values():
            for identifier, name in sources['hostAdapterNames'].items():
                plugin, skill=identifier.split(':')
                adapter=ROOT/adapter_root/name/'SKILL.md'
                target=(adapter.parent/re.search(r'canonical shared definition\]\(([^)]+)\)', adapter.read_text(encoding='utf-8')).group(1)).resolve()
                self.assertTrue(target.is_file())
                self.assertEqual(skill, target.parent.name)

if __name__ == '__main__':
    unittest.main()
