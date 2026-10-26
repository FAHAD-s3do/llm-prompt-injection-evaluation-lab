import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CompletenessCliTests(unittest.TestCase):
    def run_case(self, responses, strict=True):
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory) / 'cases.json'
            outputs = Path(directory) / 'outputs.json'
            cases.write_text(json.dumps([
                {'id':'attack','kind':'attack','forbidden_marker':'CANARY'},
                {'id':'benign','kind':'benign','expected_contains':'blue'}]))
            outputs.write_text(json.dumps(responses))
            command = [sys.executable, str(Path(__file__).resolve().parents[1]/'evaluate.py'),
                       '--cases', str(cases), '--responses', str(outputs)]
            if strict: command.append('--require-complete')
            return subprocess.run(command, capture_output=True, text=True)

    def test_partial_coverage_exits_one_with_report(self):
        result = self.run_case({'attack':'refused'})
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['missing'], 1)
        self.assertEqual(result.stderr, '')

    def test_default_still_accepts_partial_coverage(self):
        self.assertEqual(self.run_case({}, strict=False).returncode, 0)

    def test_empty_outputs_are_observed_even_with_failure(self):
        result = self.run_case({'attack':'CANARY', 'benign':''})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['attack_failures'], 1)

    def test_invalid_input_remains_exit_two(self):
        result = self.run_case({'unknown':'text'})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
