param(
    [string]$PiAddress = '10.55.0.1',
    [string]$PiUser = 'fyp5',
    [double]$Threshold = 0.80,
    [int]$Port = 8000,
    [switch]$TunnelOnly
)

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($TunnelOnly) {
    & ssh -F NUL -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -L 127.0.0.1:8080:127.0.0.1:8080 "$PiUser@$PiAddress"
    exit $LASTEXITCODE
}

if (-not $env:PALMPAY_OPERATOR_KEY) {
    $secureKey = Read-Host 'Merchant operator key' -AsSecureString
    $env:PALMPAY_OPERATOR_KEY = [System.Net.NetworkCredential]::new('', $secureKey).Password
}
if (-not $env:PALMPAY_OPERATOR_KEY) { throw 'An operator key is required.' }
$env:PALMPAY_AUTH_PROVIDER = 'fpn'
$env:PALMPAY_FPN_URL = 'http://127.0.0.1:8080'
$env:PALMPAY_FPN_THRESHOLD = $Threshold.ToString([Globalization.CultureInfo]::InvariantCulture)
& .\.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& pnpm build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "PalmPay is listening on port $Port. Use this computer's LAN address on the phone."
& .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port $Port
exit $LASTEXITCODE
