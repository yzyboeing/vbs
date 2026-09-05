import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/vbs/scripts'
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location('deps', SCRIPTS / 'check_dependencies.py')
deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deps)

import runtime_config


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

    def test_runtime_config_reports_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = runtime_config.probe_runtime(Path(tmp) / 'missing.json')
            self.assertFalse(report['configured'])
            self.assertFalse(report['ok'])
            self.assertIn('not found', report['errors'][0])

    def test_runtime_probe_accepts_matching_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            python = root / 'python'
            cli = root / 'mlx_whisper'
            model = root / 'model'
            model.mkdir()
            python.write_text('# fixture')
            cli.write_text('# fixture')
            python.chmod(0o755)
            cli.chmod(0o755)
            (model / 'config.json').write_text('{}')
            (model / 'weights.safetensors').write_bytes(b'weights')
            config = root / 'runtime.json'
            config.write_text(json.dumps({
                'schema_version': 1,
                'python_executable': str(python),
                'python_version': '3.12',
                'mlx_whisper_cli': str(cli),
                'mlx_whisper_version': '0.4.3',
                'model_id': 'mlx-community/whisper-large-v3-turbo',
                'model_revision': 'test-revision',
                'model_path': str(model),
                'weights_bytes': 7,
                'weights_sha256': 'unused-without-deep-check',
            }))
            completed = mock.Mock(returncode=0, stdout='{"python":"3.12.14","mlx_whisper":"0.4.3"}', stderr='')
            with mock.patch.object(runtime_config.subprocess, 'run', return_value=completed):
                report = runtime_config.probe_runtime(config)
            self.assertTrue(report['ok'])
            self.assertEqual(report['actual_mlx_whisper'], '0.4.3')

    def test_deep_runtime_probe_detects_model_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            python = root / 'python'
            cli = root / 'mlx_whisper'
            model = root / 'model'
            model.mkdir()
            python.write_text('# fixture')
            cli.write_text('# fixture')
            python.chmod(0o755)
            cli.chmod(0o755)
            (model / 'config.json').write_text('{}')
            (model / 'weights.safetensors').write_bytes(b'weights')
            config = root / 'runtime.json'
            config.write_text(json.dumps({
                'schema_version': 1,
                'python_executable': str(python),
                'python_version': '3.12',
                'mlx_whisper_cli': str(cli),
                'mlx_whisper_version': '0.4.3',
                'model_id': 'mlx-community/whisper-large-v3-turbo',
                'model_revision': 'test-revision',
                'model_path': str(model),
                'weights_bytes': 7,
                'weights_sha256': 'wrong',
            }))
            completed = mock.Mock(returncode=0, stdout='{"python":"3.12.14","mlx_whisper":"0.4.3"}', stderr='')
            with mock.patch.object(runtime_config.subprocess, 'run', return_value=completed):
                report = runtime_config.probe_runtime(config, deep=True)
            self.assertFalse(report['ok'])
            self.assertIn('SHA-256 mismatch', '\n'.join(report['errors']))

    def test_runtime_command_injects_configured_model(self):
        config = {'mlx_whisper_cli': '/runtime/mlx_whisper', 'model_path': '/models/large'}
        command = runtime_config.build_whisper_command(config, ['audio.wav', '--language', 'en'])
        self.assertEqual(command[-2:], ['--model', '/models/large'])
        explicit = runtime_config.build_whisper_command(
            config, ['audio.wav', '--model', 'another/model']
        )
        self.assertEqual(explicit.count('--model'), 1)


if __name__ == '__main__':
    unittest.main()
