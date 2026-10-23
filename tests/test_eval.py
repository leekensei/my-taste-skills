import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_eval", ROOT / "evaluations/run.py")
skill_eval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_eval)


class EvalTests(unittest.TestCase):
    def test_prompt_withholds_answers_and_only_with_arm_contains_skill(self):
        case = {"prompt": "Review this component", "expected": {"feature_context": False}}
        baseline = skill_eval.build_prompt(case)
        with_skill = skill_eval.build_prompt(case, "UNIQUE SKILL TEXT")
        self.assertNotIn("UNIQUE SKILL TEXT", baseline)
        self.assertIn("UNIQUE SKILL TEXT", with_skill)
        self.assertNotIn('"feature_context": false', with_skill)

    def test_grading_handles_alternatives_missing_keys_and_strict_booleans(self):
        expected = {"feature_context": False, "loading": ["conditional-mount", "query-enabled"]}
        self.assertEqual(skill_eval.grade({"reason": "Only mount the selected source", "feature_context": False, "loading": "query-enabled"}, expected)["score"], 1)
        result = skill_eval.grade({"reason": "Wrong strategy", "feature_context": 0, "loading": "suspense-only"}, expected)
        self.assertEqual(result["score"], 0)
        self.assertEqual(skill_eval.grade({"reason": "Missing decisions"}, expected)["score"], 0)
        with self.assertRaises(ValueError):
            skill_eval.grade({"feature_context": False}, expected)

    def test_fixture_regrading_computes_real_arm_delta(self):
        case = {"id": "small-api", "prompt": "Review", "expected": {"feature_context": False}}
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for arm, value in (("with", False), ("without", True)):
                path = directory / "responses" / arm / case["id"]
                path.mkdir(parents=True)
                (path / "run-1.json").write_text(json.dumps({"reason": "Synthetic harness fixture", "feature_context": value}))
            with contextlib.redirect_stdout(io.StringIO()):
                report = skill_eval.evaluate([case], "guidance", directory / "out", responses=directory / "responses")
            self.assertTrue(report["complete"])
            self.assertEqual(report["summary"]["small-api"]["delta"], 1)
            self.assertTrue((directory / "out/report.json").is_file())

    def test_runner_failure_stops_and_is_not_reported_as_a_quality_score(self):
        case = {"id": "small-api", "prompt": "Review", "expected": {"feature_context": False}}
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            report = skill_eval.evaluate([case], "guidance", Path(temp), runner=[sys.executable, "-c", "raise SystemExit(7)"])
        self.assertFalse(report["complete"])
        self.assertEqual(len(report["results"]), 1)
        self.assertIsNone(report["summary"]["small-api"]["with"])
        self.assertIsNone(report["summary"]["small-api"]["delta"])

    def test_runner_protocol_accepts_stdin_and_json_stdout(self):
        case = {"id": "small-api", "prompt": "Review", "expected": {"feature_context": False}}
        command = [sys.executable, "-c", 'import sys,json; text=sys.stdin.read(); print(json.dumps({"reason": text[:6], "feature_context": False}))']
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            report = skill_eval.evaluate([case], "guidance", Path(temp), runner=command)
        self.assertTrue(report["complete"])
        self.assertEqual(report["summary"]["small-api"]["delta"], 0)


if __name__ == "__main__":
    unittest.main()
