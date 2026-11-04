import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from create_mod import TEMPLATES, generate
from build_hmod import build


class CreateModTests(unittest.TestCase):
    def test_every_template_and_profile_builds_without_packaging_authoring_files(self):
        with tempfile.TemporaryDirectory() as folder:
            for template in TEMPLATES:
                for profile in ('balanced', 'hard'):
                    root = Path(folder) / f'{template}-{profile}'
                    generate(template, 'sample_mod', root, profile)
                    archive = build(root, root.with_suffix('.hmod'))
                    with ZipFile(archive) as package:
                        self.assertIn('horizon-mod.toml', package.namelist())
                        self.assertNotIn('balance-profile.json', package.namelist())
                        self.assertTrue(any(n.startswith('data/sample_mod/') for n in package.namelist()))

    def test_hard_profile_changes_durability_and_recipe_yield(self):
        with tempfile.TemporaryDirectory() as folder:
            for profile, damage, count in [('balanced', 240, 3), ('hard', 120, 1)]:
                root = Path(folder) / profile
                generate('survival_basics', 'sample', root, profile)
                item = json.loads((root / 'data/sample/horizon/item/field_pickaxe.json').read_text())
                recipe = json.loads((root / 'data/sample/recipe/supply_token.json').read_text())
                self.assertEqual(item['components']['minecraft:max_damage'], damage)
                self.assertEqual(recipe['result']['count'], count)

    def test_refuses_invalid_id_and_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'source'
            with self.assertRaises(ValueError):
                generate('copper_tools', '../bad', root)
            self.assertFalse(root.exists())
            root.mkdir()
            marker = root / 'keep.txt'
            marker.write_text('keep')
            with self.assertRaises(ValueError):
                generate('copper_tools', 'safe', root)
            self.assertEqual(marker.read_text(), 'keep')
