import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('artifact_eval', ROOT / 'evaluations/artifact_eval.py')
artifact_eval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact_eval)


class ArtifactEvalTests(unittest.TestCase):
    def setUp(self):
        self.case = {'id': 'example', 'task': '현재 코드 유지', 'input_code': 'const value = 1;', 'criteria': {'minimality': '불필요한 변경 없음'}}
        self.artifact = {'code': 'const value = 1;', 'explanation': '현재 요구에 충분함'}
        self.verdict = {'criteria': {'minimality': {'passed': True, 'reason': '선언을 그대로 유지함', 'evidence_source': 'result', 'evidence': 'const value = 1;'}}}

    def test_judge_is_blind_and_candidate_does_not_get_private_rubric(self):
        prompt = artifact_eval.candidate_prompt(self.case, 'UNIQUE_SKILL_TEXT')
        self.assertNotIn('불필요한 변경 없음', prompt)
        judge = artifact_eval.judge_prompt(self.case, self.artifact)
        self.assertNotIn('UNIQUE_SKILL_TEXT', judge)
        self.assertIn('const value = 1;', judge)

    def test_requires_evidence_that_exists_in_code(self):
        result = artifact_eval.grade_judgment(self.case, self.artifact, self.verdict)
        self.assertTrue(result['passed'])
        self.verdict['criteria']['minimality']['evidence'] = 'imaginary code'
        with self.assertRaises(ValueError):
            artifact_eval.grade_judgment(self.case, self.artifact, self.verdict)
        self.verdict['criteria']['minimality']['evidence_source'] = []
        with self.assertRaises(ValueError):
            artifact_eval.grade_judgment(self.case, self.artifact, self.verdict)

    def test_rejects_missing_criteria_and_nonboolean_scores(self):
        with self.assertRaises(ValueError):
            artifact_eval.grade_judgment(self.case, self.artifact, {'criteria': {}})
        self.verdict['criteria']['minimality']['passed'] = 'true'
        with self.assertRaises(ValueError):
            artifact_eval.grade_judgment(self.case, self.artifact, self.verdict)

    def test_separate_quotes_are_each_checked_against_actual_code(self):
        self.verdict['criteria']['minimality']['evidence'] = 'const value\n...\n= 1;'
        self.assertTrue(artifact_eval.grade_judgment(self.case, self.artifact, self.verdict)['passed'])
        self.verdict['criteria']['minimality']['evidence'] = 'const value\n...\nmade up code'
        with self.assertRaises(ValueError):
            artifact_eval.grade_judgment(self.case, self.artifact, self.verdict)

    def test_explanation_evidence_is_allowed_only_for_explanation_criterion(self):
        case = {**self.case, 'criteria': {'explanation': '설명과 코드 일치'}}
        judgment = {'criteria': {'explanation': {'passed': True, 'reason': '유지 이유를 설명함', 'evidence_source': 'explanation', 'evidence': self.artifact['explanation']}}}
        self.assertTrue(artifact_eval.grade_judgment(case, self.artifact, judgment)['passed'])
        self.verdict['criteria']['minimality']['evidence_source'] = 'explanation'
        self.verdict['criteria']['minimality']['evidence'] = self.artifact['explanation']
        with self.assertRaises(ValueError):
            artifact_eval.grade_judgment(self.case, self.artifact, self.verdict)

    def test_generation_review_and_report_pipeline_with_synthetic_runners(self):
        def command(payload):
            return [sys.executable, '-c', 'import sys; sys.stdin.read(); print(' + repr(json.dumps(payload, ensure_ascii=False)) + ')']
        with tempfile.TemporaryDirectory() as temp:
            report = artifact_eval.evaluate([self.case], 'guidance', command(self.artifact), command(self.verdict), Path(temp))
            self.assertTrue(report['complete'])
            self.assertEqual(report['summary']['example']['delta'], 0)
            self.assertEqual((Path(temp) / 'example/1/with/result.tsx').read_text(), self.artifact['code'])
            self.assertTrue((Path(temp) / 'report.json').is_file())


if __name__ == '__main__':
    unittest.main()
