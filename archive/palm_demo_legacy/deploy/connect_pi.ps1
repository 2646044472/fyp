param(
    [string]$UserName,
    [string]$HostName = "palm-pi.local"
)

if (-not $UserName) {
    $UserName = Read-Host "输入你在 Raspberry Pi Imager 设置的 Pi 用户名"
}

ssh "$UserName@$HostName"
