import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('deps', Path(__file__).resolve().parents[1] / 'skills/vbs/scripts/check_dependencies.py')
deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deps)


class DependencyTest(unittest.TestCase):
    def test_missing_asr_does_not_block_review_or_burn(self):
        status = deps.stage_status(True, False, True, True, False, False)
        self.assertTrue(status['review'])
        self.assertTrue(status['burn'])
        self.assertFalse(status['fetch'])
        self.assertFalse(status['asr'])

    def test_explicit_path_requires_both_entry_and_fetcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            self.assertIsNone(deps.locate_jzsub(tmp))
            (path / 'scripts').mkdir()
            (path / 'scripts/fetch_video.py').write_text('# fixture')
            self.assertIsNone(deps.locate_jzsub(tmp))
            (path / 'SKILL.md').write_text('# fixture')
            self.assertEqual(deps.locate_jzsub(tmp), path)


if __name__ == '__main__':
    unittest.main()
