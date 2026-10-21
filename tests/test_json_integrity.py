import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evaluate import load_json


class JsonIntegrityTests(unittest.TestCase):
    def test_duplicate_response_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'responses.json'
            path.write_text('{"a": "refused", "a": "CANARY"}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, "Duplicate JSON object key: 'a'"):
                load_json(path)

    def test_duplicate_nested_case_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cases.json'
            path.write_text('[{"id":"a","kind":"attack","kind":"benign"}]', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, "Duplicate JSON object key: 'kind'"):
                load_json(path)

    def test_repeated_keys_in_separate_objects_are_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cases.json'
            path.write_text('[{"id":"a"},{"id":"b"}]', encoding='utf-8')
            self.assertEqual(load_json(path), [{'id': 'a'}, {'id': 'b'}])

    def test_cli_reports_duplicate_key_without_traceback(self):
        script = Path(__file__).resolve().parents[1] / 'evaluate.py'
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory) / 'cases.json'
            responses = Path(directory) / 'responses.json'
            cases.write_text(json.dumps([{
                'id': 'a', 'kind': 'attack', 'forbidden_marker': 'CANARY'
            }]), encoding='utf-8')
            responses.write_text('{"a":"refused","a":"CANARY"}', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(script), '--cases', str(cases), '--responses', str(responses)],
                capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertIn("Duplicate JSON object key: 'a'", result.stderr)
            self.assertNotIn('Traceback', result.stderr)
