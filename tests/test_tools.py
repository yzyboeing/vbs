import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "vbs" / "scripts"

EN_A = """1
00:00:01,000 --> 00:00:03,000
Set the thrust levers to forty percent N1.

2
00:00:03,200 --> 00:00:05,000
Then wait for both engines.
"""

EN_B = """1
00:00:01,000 --> 00:00:03,000
Set thrust levers to 40 percent N1.

2
00:00:03,200 --> 00:00:05,000
Then wait for the two engines.
"""

BILINGUAL = """1
00:00:01,000 --> 00:00:03,000
Set the thrust levers to 40% N1.
将推力手柄置于 40% N1

2
00:00:03,200 --> 00:00:05,000
Then wait for both engines.
然后等待两台发动机
"""


class ToolTests(unittest.TestCase):
    def run_script(self, name, *args, check=True):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *map(str, args)],
            text=True,
            capture_output=True,
            check=check,
        )

    def test_validate_bilingual(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "bilingual.srt"
            path.write_text(BILINGUAL, encoding="utf-8")
            result = self.run_script("validate_srt.py", path, "--mode", "bilingual")
            report = json.loads(result.stdout)
            self.assertTrue(report["valid"])
            self.assertEqual(report["cue_count"], 2)

    def test_compare_asr_reports_possible_omission(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            first = root / "a.srt"
            second = root / "b.srt"
            report = root / "diff.json"
            first.write_text(EN_A, encoding="utf-8")
            second.write_text(EN_B, encoding="utf-8")
            result = self.run_script("compare_asr.py", first, second, "--json-report", report)
            self.assertIn("possible omission", result.stdout)
            self.assertGreater(json.loads(report.read_text(encoding="utf-8"))["difference_groups"], 0)

    def test_checkpoint_blocks_skipped_gate_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.bin"
            draft = root / "english-review.srt"
            approved = root / "english-approved.srt"
            source.write_bytes(b"test source")
            draft.write_text(EN_A, encoding="utf-8")
            approved.write_text(EN_A, encoding="utf-8")

            self.run_script("checkpoint.py", "init", root, "--source", source, "--route", "whisper-asr")
            self.run_script(
                "checkpoint.py", "record", root, "--stage", "english-draft-ready",
                "--artifact", f"english_review={draft}",
            )
            skipped = self.run_script(
                "checkpoint.py", "record", root, "--stage", "bilingual-draft-ready",
                check=False,
            )
            self.assertNotEqual(skipped.returncode, 0)

            self.run_script(
                "checkpoint.py", "record", root, "--stage", "english-approved",
                "--artifact", f"english_approved={approved}",
                "--approval-note", "Explicit test approval",
            )
            self.run_script("checkpoint.py", "verify", root)
            approved.write_text(EN_B, encoding="utf-8")
            tampered = self.run_script("checkpoint.py", "verify", root, check=False)
            self.assertEqual(tampered.returncode, 3)
            self.assertIn("changed after recording", tampered.stdout)

    def test_checkpoint_can_invalidate_review_and_final_outputs(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.bin"
            artifact = root / "artifact.bin"
            source.write_bytes(b"test source")
            artifact.write_bytes(b"stable artifact")

            self.run_script("checkpoint.py", "init", root, "--source", source, "--route", "whisper-asr")
            stages = [
                ("english-draft-ready", False),
                ("english-approved", True),
                ("bilingual-draft-ready", False),
                ("bilingual-approved", True),
                ("review-burn-ready", False),
                ("final-approved", True),
                ("delivered", False),
            ]
            for stage, needs_approval in stages:
                arguments = [
                    "checkpoint.py", "record", root, "--stage", stage,
                    "--artifact", f"artifact={artifact}",
                ]
                if needs_approval:
                    arguments.extend(["--approval-note", f"Approved {stage}"])
                self.run_script(*arguments)

            self.run_script("checkpoint.py", "invalidate", root, "--from", "final")
            status = json.loads(self.run_script("checkpoint.py", "status", root).stdout)
            self.assertEqual(status["current_stage"], "final-approved")
            self.assertNotIn("delivered", status["recorded_stages"])

            self.run_script("checkpoint.py", "invalidate", root, "--from", "review")
            status = json.loads(self.run_script("checkpoint.py", "status", root).stdout)
            self.assertEqual(status["current_stage"], "bilingual-approved")
            self.assertIn("bilingual-approved", status["recorded_stages"])
            self.assertNotIn("review-burn-ready", status["recorded_stages"])


if __name__ == "__main__":
    unittest.main()
