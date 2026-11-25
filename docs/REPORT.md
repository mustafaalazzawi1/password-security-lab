# Password Exposure & Defense
## A controlled offline password-auditing lab

**Mustafa Al Azzawi | 25 November 2026 | Independent educational report**

### Executive summary

This report examines what a small dictionary test can and cannot establish after a readable copy of password hashes is available. Six fictional accounts were created for the experiment. John the Ripper core 1.9.0 was run against three deliberately constructed candidate lists, each with a fresh recovery cache.

The baseline list recovered 3 of 6 accounts. Adding four predictable-pattern candidates raised recovery to 5 of 6. A final positive control deliberately included the remaining random password and recovered all 6 accounts. These are measurements of candidate coverage in this fixture, not a general crack rate or strength rating.

No real accounts, device intrusion, credential extraction, malware, or network authentication were involved. The new evidence was generated on 25 November 2026 and is separate from any earlier coursework.

### Research question and threat boundary

Question: How does the content of a candidate list affect recovery of salted password hashes?

The starting assumption is that the auditor already has readable hashes. The lab does not establish how they were obtained. Physical possession of a device does not automatically imply readable hashes or administrator access. An unlocked session, an exposed backup, or insufficiently protected data can create different exposure paths; none was tested here.

The experiment distinguishes three things: hash exposure, offline verification of candidate passwords, and possible later account misuse. Only the middle step was executed.

### Method

- Platform: Linux x86_64; Python 3; OpenSSL 3.5.9; John core 1.9.0.
- Scheme: SHA-512-crypt, encoded with the `$6$` prefix; OpenSSL's default 5,000 rounds. Chosen for compatibility in this teaching lab, not for new production storage.
- Six unique, deterministic fixture salts; two accounts deliberately share the same plaintext. Their hashes differ.
- One 24-character comparison password is generated using Python's `secrets` module. All fixture plaintexts are recorded and intentionally public.
- Six candidates in the baseline; ten in the expanded list; eleven in the positive control.
- No mangling rules, GPU, brute-force mode, remote targets, or performance tuning.
- A separate local binary/config directory and initially absent pot file for each run prevent cache carry-over.
- Raw standard output, standard error, `--show` results, candidate lists, and input digests are preserved.

### Results

| Fixture | Pattern | Baseline | Expanded | Positive control |
| --- | --- | --- | --- | --- |
| lab_numeric | Common numeric sequence | Recovered | Recovered | Recovered |
| lab_dictionary | Common dictionary word | Recovered | Recovered | Recovered |
| lab_season | Season/year/symbol | Not recovered | Recovered | Recovered |
| lab_context | Fictional name/year/symbol | Not recovered | Recovered | Recovered |
| lab_reuse | Reused dictionary word | Recovered | Recovered | Recovered |
| lab_random | Generated 24 characters | Not recovered | Not recovered | Recovered |

The positive control is intentionally different: its list contains the known random plaintext. It checks that the hash and verification path work; it does not demonstrate guessing an unknown random secret. The first two lists were selected to contain the other examples, so the exercise is educational rather than representative.

The runner passed 23 fixture/result assertions. A separate verifier checked raw recovered values, identical hash inputs across runs, candidate counts, checksums, and summary consistency. These checks validate the experiment's records, not the security of an organization.

### Defensive interpretation

Salts cause identical passwords to have different hashes, but a known candidate can still be verified. Password predictability matters even when a password contains uppercase letters, digits, and punctuation. Long, unique generated passwords, protected hash access, and a suitable costly salted password-hashing scheme address different parts of this risk [2].

Online rate limits and MFA protect authentication services; neither changes the ability to compare guesses with an already exposed hash copy. MFA can still help limit misuse of a recovered password. These controls were not tested here [2].

For device exposure, disk encryption helps protect data at rest when keys remain protected [3]. Avoiding unknown removable media reduces one exposure path [4]. Encryption is not a blanket defense for an already unlocked or compromised session. The report does not claim to defeat FileVault, USB security, MFA, or any operating-system protection.

### Practical review checklist

| Area | Review action | Evidence to collect in a real authorized assessment |
| --- | --- | --- |
| Device handling | Confirm screen lock, approved media policy, and loss-reporting process. | Policy and non-sensitive configuration evidence. |
| Data at rest | Confirm encryption status and recovery-key handling. | Verified setting and recovery procedure, not the key itself. |
| Hash storage | Review permissions, algorithm, work factor, and backup access. | Configuration and design review. |
| Password choice | Support unique generated passwords and reject known weak choices. | Policy and controlled test-account checks. |
| Authentication | Review MFA and online rate limiting separately. | Authorized test plan and authentication logs. |

These are proposed review actions. No control was enabled, bypassed, or validated on Mustafa's devices.

### Limitations

Only six constructed accounts and eleven total distinct candidates were used. Recovery is determined by which fixture passwords appear in the selected lists. Failure to recover a password does not establish that it is secure. No exhaustive search, entropy measurement, time-to-crack estimate, hardware comparison, population statistics, or real-world exploit was performed. John console speeds are incidental and should not be quoted as a benchmark. The lab's legacy-compatible hash configuration is not a deployment recommendation.

### Reproduction and provenance

The companion ZIP contains `run_lab.py`, `verify_evidence.py`, setup instructions, original run evidence, and Arabic interview notes. Run `bash scripts/setup-john.sh`, then `python3 run_lab.py --john-dir tools/john-1.9.0/run --output evidence/my-new-run`, and validate with `python3 verify_evidence.py evidence/my-new-run`.

Each reproduction creates a new random comparison and must use a new output directory. Expected recovery counts remain 3, 5, and 6; hashes and random plaintexts will differ. The setup downloads the official John source and checks a pinned observed SHA-256. It does not claim independent GPG verification.

This independent report was prepared for Mustafa Al Azzawi with Codex assistance. The new code and experiments were executed in the assistant's Linux environment under his direction. Earlier presentation files are not republished and no historical results are invented. Mustafa should reproduce the lab and understand its limitations before using it as an interview demonstration.

### References

[1] Openwall. John the Ripper command-line options and wordlist mode. https://www.openwall.com/john/doc/OPTIONS.shtml and https://www.openwall.com/john/doc/MODES.shtml

[2] NIST. SP 800-63B-4, Password Verifiers and Appendix A. https://pages.nist.gov/800-63-4/sp800-63b.html

[3] Apple Platform Security. Volume encryption with FileVault. https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/1/web/1

[4] CISA. The Risks of Using Portable Devices. https://www.cisa.gov/sites/default/files/publications/RisksOfPortableDevices.pdf

Sources checked 25 November 2026. This educational report is not a compliance certification.
