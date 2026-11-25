#!/usr/bin/env python3
"""Cross-check recorded raw output, wordlists and summary without rerunning John."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
s = json.loads((root/'summary.json').read_text())
fixtures = json.loads((root/'fixtures.json').read_text())
by_name = {f['account']: f for f in fixtures}
hashes = (root/'fixtures.sha512crypt').read_bytes()
assert hashlib.sha256(hashes).hexdigest() == s['fixture_sha256']
assert len(fixtures) == len(by_name) == 6
assert hashes.decode() == ''.join(f"{f['account']}:{f['hash']}\n" for f in fixtures)
for stage in s['stages']:
    d = root/stage['stage']
    words = (d/'wordlist.txt').read_text().splitlines()
    assert len(words) == len(set(words)) == stage['candidates']
    assert hashlib.sha256((d/'wordlist.txt').read_bytes()).hexdigest() == stage['wordlist_sha256']
    assert (d/'fixtures.sha512crypt').read_bytes() == hashes
    recovered = dict(line.split(':',1) for line in (d/'show.txt').read_text().splitlines() if line.startswith('lab_'))
    expected = {f['account']:f['password'] for f in fixtures if f['password'] in words}
    assert recovered == expected
    assert sorted(recovered) == stage['accounts']
    assert len(recovered) == stage['recovered']
    assert 'Session completed' in (d/'run.txt').read_text()
assert [x['recovered'] for x in s['stages']] == [3,5,6]
assert s['checks_passed'] == len(s['checks']) == 23
print(json.dumps({'status':'PASS','stages_checked':3,'input_hashes_equal_across_stages':True,
                  'raw_show_matches_summary_and_wordlist_coverage':True,'fixture_assertions_passed':23},indent=2))
