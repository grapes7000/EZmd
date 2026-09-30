#!/usr/bin/env python3
"""Run EZmd's complete repository health gate on every supported desktop platform.

This file contains the checking logic so Linux, macOS, Windows, developers, and CI all execute
the same steps. Platform-specific launchers must stay thin and must not duplicate check logic.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*command: str) -> None:
    """Run one check from the repository root and fail immediately if it fails."""
    print(f"==> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def git_output(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def check_secret_filenames() -> None:
    """Reject a deliberately small set of filenames that commonly contain credentials."""
    tracked = git_output("ls-files").splitlines()
    unsafe: list[str] = []
    secret_suffixes = {".key", ".pem", ".p12", ".pfx"}
    for raw_path in tracked:
        path = Path(raw_path)
        name = path.name.lower()
        if name == ".env.example":
            continue
        if (
            name == ".env"
            or name.startswith(".env.")
            or path.suffix.lower() in secret_suffixes
        ):
            unsafe.append(raw_path)

    if unsafe:
        for path in unsafe:
            print(path, file=sys.stderr)
        raise SystemExit("ERROR: Potential secret-bearing files are tracked by Git.")


def require_program(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"ERROR: {name} is required to run repository checks.")


def main() -> int:
    require_program("git")
    if not (ROOT / "uv.lock").is_file():
        raise SystemExit("ERROR: uv.lock is missing. Run 'uv lock' intentionally and review it.")

    run("git", "diff", "--check")
    print("==> Check obvious secret-bearing filenames", flush=True)
    check_secret_filenames()
    run("ruff", "check", ".")
    run("ruff", "format", "--check", ".")
    run("basedpyright")
    run("pytest", "--cov=ezmd", "--cov-report=term-missing")
    run(sys.executable, "-c", "import ezmd")
    print("==> All checks passed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
