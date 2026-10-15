# Validation — 2026-10-15

- 11 unittest cases passed on Python 3.9 and 3.12 locally. Development tooling requires Python 3.10+.
- coverage.py: 78% overall statements; model module 100%. CLI subprocess execution is not included in the parent coverage count.
- Synthetic evaluation: 12/16 accepted, 12/12 accepted correct, 4/4 unknowns abstained. These are smoke-test results only.
- Ruff lint and format checks passed.
- Bandit reported zero issues in application code.
- Runtime dependency audit: no third-party packages and no known vulnerabilities reported.
- Gitleaks directory scan reported no secrets. Full-history scanning is also run before push and in CI.
- MIT license and provenance documentation reviewed; no external datasets, weights, or artwork bundled.
- GitHub Actions results are available from the README badges; local results do not imply hosted CI success until those runs complete.
