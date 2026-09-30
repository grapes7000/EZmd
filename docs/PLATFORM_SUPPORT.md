# Platform Support

## Product requirement

EZmd is a cross-platform desktop application.

The supported platform families are:

- Linux;
- macOS;
- Windows.

Exact minimum OS versions and packaging formats are release decisions and are not frozen in
Build 01. Source behavior and tests must remain portable across all three families from the start.

## Python and Qt baseline

- Minimum Python: 3.12.
- UI toolkit: PySide6 / Qt 6.
- Runtime dependency range begins with PySide6 6.11 and stays below Qt 7 until an explicit
  compatibility decision changes it.

The lockfile selects the exact development version; project metadata keeps a compatible range.

## Cross-platform coding rules

Production code must:

- use `pathlib` or Qt path/file APIs instead of splitting path strings manually;
- avoid hard-coded `/tmp`, `/home`, drive letters, or path separators;
- avoid Bash/PowerShell-specific logic in application code;
- use Qt standard shortcuts/actions where practical instead of platform-specific key strings;
- handle paths containing spaces and Unicode;
- avoid relying on filesystem case sensitivity;
- keep platform-specific behavior isolated and justified when it is genuinely unavoidable.

Do not add OS-detection branches when Qt or Python already provides a portable operation.

## Document I/O rules

- User text is UTF-8 unless a later file-format decision explicitly expands encoding support.
- Tests must include paths with spaces and non-ASCII characters.
- Opening/saving must never depend on the current working directory.
- Save failure must not replace the current in-memory document with partial/empty content.
- Build 01 intentionally writes LF (`\n`) line endings on every platform. Build 03 owns the broader
  Markdown round-trip/newline-preservation contract.

## Testing

GitHub Actions runs the repository health gate on Linux, macOS, and Windows.

Qt tests run without a visible desktop in CI. UI tests must not depend on pixel-perfect screenshots,
window-manager decorations, font rasterization, or timing assumptions that differ by platform.

Use pytest temporary directories for filesystem tests. Never point automated tests at real user
configuration or document locations.

## Developer tooling

The quality-check logic is Python so the same implementation works on every platform:

```text
bin/check.py
```

Canonical gate:

```text
uv run --locked python bin/check.py
```

Convenience launchers may exist for POSIX shells and PowerShell, but they must remain thin and
must not contain separate quality logic.

## Packaging

Creating distributable executables/installers is intentionally deferred. Do not introduce
PyInstaller, Nuitka, Briefcase, platform installers, code signing, notarization, or updater logic
inside early feature builds unless a later build contract explicitly adds packaging.
