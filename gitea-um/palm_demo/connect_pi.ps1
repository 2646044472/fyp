param(
    [string]$UserName,
    [string]$HostName = "palm-pi.local"
)

if (-not $UserName) {
    $UserName = Read-Host "Enter the Pi username configured in Raspberry Pi Imager"
}

ssh "$UserName@$HostName"
