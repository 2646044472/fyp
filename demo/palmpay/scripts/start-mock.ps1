param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not $env:PALMPAY_OPERATOR_KEY) {
    $secureKey = Read-Host 'Merchant operator key' -AsSecureString
    $env:PALMPAY_OPERATOR_KEY = [System.Net.NetworkCredential]::new('', $secureKey).Password
}
if (-not $env:PALMPAY_OPERATOR_KEY) { throw 'An operator key is required.' }
$env:PALMPAY_DEMO = '1'
$env:PALMPAY_AUTH_PROVIDER = 'mock'
& .\.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& pnpm build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "PalmPay mock demo is listening on port $Port."
& .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port $Port
exit $LASTEXITCODE
