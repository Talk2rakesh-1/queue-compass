# Security

Report a vulnerability using this repository’s GitHub private vulnerability reporting feature. Do not include real personal data or credentials in public issues. Version 0.1 is the supported MVP line.

No credentials, remote model calls, telemetry, or third-party runtime packages are required. The app/CLI does not execute user text. CI has read-only repository permissions and pins actions to commits. A full-history Gitleaks scan runs on pushes and pull requests. Automated scanning is evidence, not a guarantee of security.

Ticket text remains on your machine, but output includes words from the ticket: treat output and redirected files as sensitive. Training and input JSON are capped at 2 MB; each text is capped at 10,000 characters. Only JSON is parsed; no pickle model loading. No server is exposed. This is an English bag-of-words model, vulnerable to distribution shift and adversarial keyword stuffing. Never use routing suggestions to suppress incidents, determine severity, or take privileged actions. Human review is mandatory. Use an actively supported Python version for deployment; local compatibility was also tested on the host’s Python 3.9.
