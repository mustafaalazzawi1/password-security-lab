#!/usr/bin/env python3
"""Validate recorded teaching evidence without running John or using the network."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

STAGES = ('01-baseline', '02-patterns', '03-positive-control')
COUNTS = (3, 5, 6)


class EvidenceError(ValueError):
    """Missing, malformed, or inconsistent evidence."""


def require(condition, message):
    # Unlike assert, this validation is also active under python -O.
    if not condition:
        raise EvidenceError(message)


def read_bytes(path):
    try:
        return path.read_bytes()
    except OSError as error:
        raise EvidenceError(f'{path.name}: cannot read evidence ({error.strerror})') from error


def read_text(path):
    try:
        return read_bytes(path).decode('utf-8')
    except UnicodeError as error:
        raise EvidenceError(f'{path.name}: expected UTF-8 text') from error


def read_json(path):
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as error:
        raise EvidenceError(f'{path.name}: invalid JSON') from error


def verify_evidence(root):
    """Check the six-account, three-stage fixture and return a JSON-ready result."""
    root = Path(root)
    summary = read_json(root / 'summary.json')
    fixtures = read_json(root / 'fixtures.json')
    require(isinstance(summary, dict), 'summary.json: expected an object')
    require(isinstance(fixtures, list) and len(fixtures) == 6, 'fixtures.json: expected six fixtures')
    by_name = {}
    for fixture in fixtures:
        require(isinstance(fixture, dict), 'fixtures.json: expected fixture objects')
        for key in ('account', 'password', 'salt', 'hash'):
            require(isinstance(fixture.get(key), str) and fixture[key], f'fixtures.json: invalid {key}')
        account = fixture['account']
        require(account.startswith('lab_') and all(c.isalnum() or c == '_' for c in account),
                'fixtures.json: invalid fictional account name')
        require(account not in by_name, 'fixtures.json: duplicate account')
        require('\n' not in fixture['password'] and '\r' not in fixture['password'],
                'fixtures.json: multiline password')
        require(fixture['hash'].startswith('$6$' + fixture['salt'] + '$'),
                'fixtures.json: salt and hash disagree')
        by_name[account] = fixture
    require(len({f['salt'] for f in fixtures}) == 6, 'fixtures.json: salts must be unique')
    hashes = read_bytes(root / 'fixtures.sha512crypt')
    require(hashlib.sha256(hashes).hexdigest() == summary.get('fixture_sha256'),
            'fixtures.sha512crypt: checksum mismatch')
    expected_hashes = ''.join(f"{f['account']}:{f['hash']}\n" for f in fixtures).encode()
    require(hashes == expected_hashes, 'fixtures.sha512crypt: fixture manifest mismatch')
    stages = summary.get('stages')
    require(isinstance(stages, list) and len(stages) == 3, 'summary.json: expected all three stages')
    require(all(isinstance(stage, dict) for stage in stages), 'summary.json: invalid stage')
    require(tuple(stage.get('stage') for stage in stages) == STAGES,
            'summary.json: unexpected stage names or order')
    # Resolve only fixed, validated stage names, never arbitrary manifest paths.
    for stage, expected_count in zip(stages, COUNTS):
        name = stage['stage']
        directory = root / name
        for key in ('candidates', 'recovered', 'total'):
            require(type(stage.get(key)) is int, f'{name}: {key} must be an integer')
        require(stage['total'] == 6 and stage['recovered'] == expected_count,
                f'{name}: unexpected recovery counts')
        words = read_text(directory / 'wordlist.txt').splitlines()
        require(all(words) and len(words) == len(set(words)) == stage['candidates'],
                f'{name}: candidate count, blanks or duplicate candidates')
        require(hashlib.sha256(read_bytes(directory / 'wordlist.txt')).hexdigest()
                == stage.get('wordlist_sha256'), f'{name}: wordlist checksum mismatch')
        require(read_bytes(directory / 'fixtures.sha512crypt') == hashes,
                f'{name}: hash inputs differ between stages')
        recovered = {}
        for line in read_text(directory / 'show.txt').splitlines():
            if not line.startswith('lab_'):
                continue
            require(':' in line, f'{name}: malformed recovered account')
            account, password = line.split(':', 1)
            require(account in by_name, f'{name}: unknown recovered account')
            require(account not in recovered, f'{name}: duplicate recovered account')
            recovered[account] = password
        expected = {f['account']: f['password'] for f in fixtures if f['password'] in words}
        require(recovered == expected, f'{name}: raw recovery differs from candidate coverage')
        require(sorted(recovered) == stage.get('accounts'), f'{name}: account summary mismatch')
        require(len(recovered) == stage['recovered'], f'{name}: recovery summary mismatch')
        require('Session completed' in read_text(directory / 'run.txt'), f'{name}: missing completion record')
    checks = summary.get('checks')
    require(isinstance(checks, list) and len(checks) == 23
            and all(isinstance(check, str) and check for check in checks)
            and len(set(checks)) == 23 and type(summary.get('checks_passed')) is int
            and summary['checks_passed'] == 23, 'summary.json: invalid recorded assertion list')
    return {'status': 'PASS', 'stages_checked': 3, 'input_hashes_equal_across_stages': True,
            'raw_show_matches_summary_and_wordlist_coverage': True, 'recorded_fixture_assertions': 23}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence_directory', type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify_evidence(args.evidence_directory)
    except EvidenceError as error:
        print(f'Evidence verification failed: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
