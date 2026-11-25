# Provenance and claim boundaries

**Report owner:** Mustafa Al Azzawi. **Prepared:** 25 November 2026.

This is a new, independent educational report. The user requested a password/physical-security portfolio project, later supplied an earlier presentation as background, and requested an independent report under his name. The earlier slides are preserved separately and are not republished or modified in this package.

Codex prepared the new reproduction harness, ran the synthetic experiments in a Linux environment, and drafted the analysis and report under Mustafa's direction. This package does not claim Mustafa personally executed these new commands before reviewing it. It does not imply the newly measured results were obtained during an earlier course.

The earlier presentation is not evidence of real data exfiltration, a remote shell, device compromise, or a completed password audit. The current experiment starts at a supplied readable hash copy and demonstrates candidate verification only. It does not recreate an unknown-USB payload.

## Tool provenance

- John the Ripper **core 1.9.0**, built from the official Openwall source with `make -j2 linux-x86-64`.
- Archive: `https://download.openwall.net/pub/projects/john/1.9.0/john-1.9.0.tar.xz`.
- Observed SHA-256: `0b266adcfef8c11eed690187e71494baea539efbd632fe221181063ba09508df`.
- This digest pins the fetched archive for reproducibility; it is not a claim of independent GPG signature verification.
- John uses the host's generic `crypt(3)` implementation for these `$6$` fixtures. OpenSSL creates the hashes; its exact version is in the evidence.
- No GPU, distributed cracking, rules engine, stolen dataset, or performance tuning was used.

## Public copy contents

Only synthetic accounts, public demonstration passwords, new analysis, references, and code. The source presentations, private email address, desktop screenshots, and unrelated projects are excluded. No external service, account permission, or GitHub repository was changed to run this lab.
