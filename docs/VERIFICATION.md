# Verification record

Verified on 25 November 2026 in Linux x86_64.

- Extracted the source ZIP into a fresh directory.
- Ran the included setup script: downloaded the official John core archive, matched the pinned SHA-256, and compiled successfully.
- Re-executed the extracted runner with that newly compiled tool. Recovery counts were 3/6, 5/6, and 6/6; all 23 fixture/result assertions passed.
- The separate evidence verifier passed for both the packaged original run and the fresh run.
- Visually inspected all five pages of the PDF after embedding fonts.
- Tested the website's three recorded stages; all counts and account outcomes matched the saved summary.
- Tested quiz scoring (4/5 and 5/5), explanations, reset, cleared feedback after answer changes, required answers, and keyboard activation.
- Checked desktop layout and 390px/768px iframe layouts in Chromium. No horizontal document overflow was observed. These were responsive viewport checks, not physical mobile-device tests.
- Checked local HTML assets and download targets.

The interactive web page displays saved evidence and performs a local educational quiz. It does not run John, accept user passwords, contact a login service, or save quiz scores. macOS execution of the lab and Safari were not tested.

Fresh setup/run timestamp (UTC): 2026-11-25T07:03:14.108849+00:00

## Evidence-verifier maintenance — 25 November 2026

Added a callable validator with explicit errors and a CLI, 22 independent regression cases, and read-only GitHub Actions. The suite passes in normal and optimized Python. Original experiment inputs, outputs, report results, and the 23 recorded assertions remain unchanged. The new tests validate the evidence pipeline, not password security in a real deployment.
