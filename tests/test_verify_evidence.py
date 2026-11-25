"""Test valid records and independently damaged copies; never modify saved evidence."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from verify_evidence import EvidenceError, verify_evidence

PROJECT = Path(__file__).resolve().parents[1]
RECORDED = PROJECT / 'evidence' / 'run-20261125'


class EvidenceVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'run'
        shutil.copytree(RECORDED, self.root)

    def mutate_json(self, name, mutation):
        path = self.root / name
        value = json.loads(path.read_text())
        mutation(value)
        path.write_text(json.dumps(value))

    def replace_text(self, name, old, new):
        path = self.root / name
        path.write_text(path.read_text().replace(old, new))

    def append(self, name, text):
        with (self.root / name).open('a') as handle:
            handle.write(text)

    def test_recorded_run_passes(self):
        result = verify_evidence(self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['stages_checked'], 3)

    def test_optimized_python_still_rejects_invalid_evidence(self):
        (self.root / 'fixtures.sha512crypt').write_text('tampered')
        result = subprocess.run([sys.executable, '-O', str(PROJECT / 'verify_evidence.py'), str(self.root)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn('checksum mismatch', result.stderr)
        self.assertNotIn('Traceback', result.stderr)


# Each case changes a different observable input or summary contract.
CASES = [
 ('missing_file', lambda t: (t.root/'01-baseline/show.txt').unlink(), 'cannot read evidence'),
 ('invalid_json', lambda t: (t.root/'summary.json').write_text('{'), 'invalid JSON'),
 ('wrong_json_shape', lambda t: (t.root/'summary.json').write_text('[]'), 'expected an object'),
 ('invalid_utf8', lambda t: (t.root/'01-baseline/show.txt').write_bytes(b'\xff'), 'UTF-8'),
 ('duplicate_fixture', lambda t: t.mutate_json('fixtures.json', lambda d: d.__setitem__(1,d[0])), 'duplicate account'),
 ('hash_checksum', lambda t: t.append('fixtures.sha512crypt','changed'), 'checksum mismatch'),
 ('manifest_password', lambda t: t.mutate_json('fixtures.json',lambda d:d[0].update(password='changed')), 'candidate coverage'),
 ('missing_stage', lambda t: t.mutate_json('summary.json',lambda d:d['stages'].pop()), 'all three stages'),
 ('stage_path', lambda t: t.mutate_json('summary.json',lambda d:d['stages'][0].update(stage='../outside')), 'stage names or order'),
 ('reordered_stages', lambda t: t.mutate_json('summary.json',lambda d:d['stages'].reverse()), 'stage names or order'),
 ('invalid_numeric_type', lambda t: t.mutate_json('summary.json',lambda d:d['stages'][0].update(candidates=True)), 'must be an integer'),
 ('changed_wordlist', lambda t: t.replace_text('01-baseline/wordlist.txt','qwerty','qwertz'), 'wordlist checksum'),
 ('duplicate_candidate', lambda t: t.append('01-baseline/wordlist.txt','password\n'), 'duplicate candidates'),
 ('different_hash_inputs', lambda t: (t.root/'02-patterns/fixtures.sha512crypt').write_text('different'), 'hash inputs differ'),
 ('wrong_plaintext', lambda t: t.replace_text('01-baseline/show.txt','lab_numeric:123456','lab_numeric:000000'), 'candidate coverage'),
 ('duplicate_recovery', lambda t: t.append('01-baseline/show.txt','\nlab_numeric:123456\n'), 'duplicate recovered account'),
 ('unknown_recovery', lambda t: t.append('01-baseline/show.txt','\nlab_unknown:123456\n'), 'unknown recovered account'),
 ('summary_accounts', lambda t: t.mutate_json('summary.json',lambda d:d['stages'][0].update(accounts=[])), 'account summary'),
 ('incomplete_execution', lambda t: t.replace_text('01-baseline/run.txt','Session completed','Session interrupted'), 'completion record'),
 ('assertion_list', lambda t: t.mutate_json('summary.json',lambda d:d.update(checks_passed=24)), 'assertion list'),
]


def make_case(mutation, reason):
    def test(self):
        mutation(self)
        with self.assertRaisesRegex(EvidenceError, reason):
            verify_evidence(self.root)
    return test


for name, mutation, reason in CASES:
    setattr(EvidenceVerificationTests, 'test_' + name, make_case(mutation, reason))

if __name__ == '__main__':
    unittest.main()
