#!/usr/bin/env python3
"""Reproduce this portfolio lab using only generated, fictional credentials."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import shlex
import shutil
import subprocess
import sys


def run_lab(john_dir, output):
    john_dir = john_dir.resolve()
    output = output.resolve()
    if output.exists():
        raise ValueError('Output must be a new directory; earlier evidence is preserved.')
    if not (john_dir / 'john').is_file() or not (john_dir / 'john.conf').is_file():
        raise ValueError('Use the run directory of the locally built John 1.9.0 core source.')
    if not shutil.which('openssl'):
        raise ValueError('OpenSSL is required.')
    output.mkdir(parents=True)
    env = dict(os.environ, LC_ALL='C', OMP_NUM_THREADS='1', TZ='UTC')
    identities = [
        ('lab_numeric', 'Common numeric sequence', '123456'),
        ('lab_dictionary', 'Common dictionary word', 'password'),
        ('lab_season', 'Season/year/symbol pattern', 'Summer2026!'),
        ('lab_context', 'Fictional name/year/symbol pattern', 'Orion1998!'),
        ('lab_reuse', 'Same password, different salt', 'password'),
        ('lab_random', 'Generated 24-character comparison', secrets.token_urlsafe(18)),
    ]
    manifest = []
    for account, category, password in identities:
        salt = hashlib.sha256(account.encode()).hexdigest()[:16]
        hashed = subprocess.run(['openssl', 'passwd', '-6', '-salt', salt, '-stdin'],
                                input=password+'\n', capture_output=True, text=True,
                                env=env, check=True, timeout=10).stdout.strip()
        assert hashed.startswith('$6$')
        manifest.append(dict(account=account, category=category, password=password,
                             salt=salt, hash=hashed))
    (output / 'fixtures.json').write_text(json.dumps(manifest, indent=2)+'\n')
    hashes = ''.join(f"{m['account']}:{m['hash']}\n" for m in manifest)
    (output / 'fixtures.sha512crypt').write_text(hashes)
    basic = ['password', '123456', 'qwerty', 'letmein', 'welcome', 'admin']
    expanded = basic + ['Summer2026!', 'Winter2026!', 'Orion1998!', 'Orion2026!']
    stages = [
        ('01-baseline', basic, {'lab_numeric', 'lab_dictionary', 'lab_reuse'}),
        ('02-patterns', expanded, {'lab_numeric', 'lab_dictionary', 'lab_reuse', 'lab_season', 'lab_context'}),
        ('03-positive-control', expanded + [identities[-1][2]], {x[0] for x in identities}),
    ]
    checks = []
    def require(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    require(len({m['salt'] for m in manifest}) == 6, 'Six unique fixture salts')
    require(manifest[1]['hash'] != manifest[4]['hash'], 'Identical passwords yield different salted hashes')
    require(identities[-1][2] not in expanded, 'Random comparison excluded from both attack wordlists')
    results = []
    for name, words, expected in stages:
        stage = output / name
        stage.mkdir()
        # Core, non-systemwide build resolves its pot/config beside argv[0].
        shutil.copy2(john_dir/'john', stage/'john')
        shutil.copy2(john_dir/'john.conf', stage/'john.conf')
        (stage/'wordlist.txt').write_text('\n'.join(words)+'\n')
        (stage/'fixtures.sha512crypt').write_text(hashes)
        require(not (stage/'john.pot').exists(), f'{name}: clean pot before execution')
        cmd = ['./john', '--format=crypt', '--wordlist=wordlist.txt', 'fixtures.sha512crypt']
        proc = subprocess.run(cmd, cwd=stage, env=env, capture_output=True,
                              text=True, check=True, timeout=60)
        (stage/'run.txt').write_text('$ '+shlex.join(cmd)+'\n\nSTDOUT\n'+proc.stdout+'\nSTDERR\n'+proc.stderr)
        showcmd = ['./john', '--show', '--format=crypt', 'fixtures.sha512crypt']
        shown = subprocess.run(showcmd, cwd=stage, env=env, capture_output=True,
                               text=True, check=True, timeout=15)
        (stage/'show.txt').write_text('$ '+shlex.join(showcmd)+'\n\n'+shown.stdout+shown.stderr)
        recovered = {}
        for line in shown.stdout.splitlines():
            if line.startswith('lab_'):
                account, password = line.split(':', 1)
                recovered[account] = password
        require(set(recovered) == expected, f'{name}: observed accounts match the declared candidate coverage')
        for account, password in recovered.items():
            require(password == next(x[2] for x in identities if x[0] == account), f'{name}: verified plaintext for {account}')
        results.append(dict(stage=name, candidates=len(words), recovered=len(recovered), total=6,
                            accounts=sorted(recovered), wordlist_sha256=hashlib.sha256((stage/'wordlist.txt').read_bytes()).hexdigest()))
        # Do not redistribute John or its configuration in the evidence package.
        (stage/'john').unlink()
        (stage/'john.conf').unlink()
    version = subprocess.run([str(john_dir/'john')], capture_output=True, text=True, env=env, timeout=10)
    john_version = (version.stdout + version.stderr).splitlines()[0]
    openssl_version = subprocess.run(['openssl', 'version'], capture_output=True, text=True, check=True).stdout.strip()
    summary = dict(executed_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                   platform=dict(system=platform.system(), machine=platform.machine()),
                   python=sys.version.split()[0], john=john_version, openssl=openssl_version,
                   hash_scheme='SHA-512-crypt ($6$), OpenSSL default 5000 rounds; teaching fixture, not a deployment recommendation',
                   fixture_sha256=hashlib.sha256(hashes.encode()).hexdigest(), stages=results,
                   checks_passed=len(checks), checks=checks,
                   limitations=['Constructed six-account fixture, not a representative sample.',
                                'Wordlists intentionally contain selected fixture passwords.',
                                'Positive control deliberately includes the random plaintext.',
                                'No rate comparison, brute-force estimate, real-account test, physical intrusion, or defense efficacy test.'])
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('executed_at_utc','john','stages','checks_passed')}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--john-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run_lab(args.john_dir, args.output)
