"""Enforce this MVP's licensed-source / no runtime dependencies policy."""

import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[1]
errors = []
for name in ("LICENSE", "THIRD_PARTY.md", "SECURITY.md"):
    if not (root / name).is_file():
        errors.append(f"Missing {name}")
if "MIT License" not in (root / "LICENSE").read_text():
    errors.append("Expected MIT license")
if (root / "requirements.txt").exists():
    if any(
        line.strip() and not line.startswith("#")
        for line in (root / "requirements.txt").read_text().splitlines()
    ):
        errors.append("Runtime dependencies require a new license/security review")
if (root / "Package.swift").exists():
    if ".package(" in (root / "Package.swift").read_text():
        errors.append("External Swift packages require a new license/security review")
if errors:
    sys.exit("\n".join(errors))
print("License documents present; declared runtime dependency boundary verified.")
