import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from evaluate import evaluate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.attack = {'id': 'a', 'kind': 'attack', 'forbidden_marker': 'CANARY'}
        self.benign = {'id': 'b', 'kind': 'benign', 'expected_contains': 'blue'}

    def test_invalid_suite_shapes(self):
        for cases in (None, {}, [], 'text', [None], [[]]):
            with self.subTest(cases=cases), self.assertRaises(ValueError):
                evaluate(cases, {})

    def test_invalid_ids(self):
        for value in (None, '', '  ', 1, []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate([dict(self.attack, id=value)], {})

    def test_empty_or_invalid_criteria_rejected_even_when_missing(self):
        for case, field in ((self.attack, 'forbidden_marker'), (self.benign, 'expected_contains')):
            for value in ('', '  ', None, 42, []):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    evaluate([dict(case, **{field: value})], {})

    def test_missing_criterion(self):
        with self.assertRaises(ValueError): evaluate([{'id':'a','kind':'attack'}], {})

    def test_response_mapping_required(self):
        for responses in (None, [], 'text'):
            with self.subTest(responses=responses), self.assertRaises(ValueError):
                evaluate([self.attack], responses)

    def test_unknown_response_rejected(self):
        with self.assertRaises(ValueError): evaluate([self.attack], {'typo':'CANARY'})

    def test_null_response_is_not_missing(self):
        with self.assertRaises(ValueError): evaluate([self.attack], {'a':None})

    def test_empty_output_is_observed(self):
        result=evaluate([self.attack,self.benign], {'a':'','b':''})
        self.assertEqual(result['missing'],0)
        self.assertEqual(result['cases'][1]['status'],'utility_fail')
        self.assertEqual(result['coverage']['attack']['rate'],1)

    def test_partial_coverage(self):
        result=evaluate([self.attack,dict(self.attack,id='a2'),self.benign], {'a':'refusal'})
        self.assertEqual(result['coverage']['attack'],dict(total=2,observed=1,missing=1,rate=0.5))
        self.assertEqual(result['coverage']['benign']['rate'],0)
        self.assertEqual(result['observed_failure_rate'],0)

    def test_absent_category_rate_is_null(self):
        result=evaluate([self.benign], {'b':'blue'})
        self.assertIsNone(result['coverage']['attack']['rate'])

    def test_cli_invalid_input_clean_error(self):
        script=Path(__file__).resolve().parents[1]/'evaluate.py'
        with tempfile.TemporaryDirectory() as directory:
            cases=Path(directory)/'cases.json'; responses=Path(directory)/'responses.json'
            cases.write_text(json.dumps([self.attack])); responses.write_text('[]')
            result=subprocess.run([sys.executable,str(script),'--cases',str(cases),'--responses',str(responses)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertEqual(result.stdout,'')
            self.assertNotIn('Traceback',result.stderr)
