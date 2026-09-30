# Windows PowerShell convenience launcher. The real cross-platform gate lives in bin/check.py.
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
uv run --locked python bin/check.py
exit $LASTEXITCODE
