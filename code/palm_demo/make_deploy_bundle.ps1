$appRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputDir = Join-Path $appRoot "dist"
$archive = Join-Path $outputDir "palm_demo_pi.zip"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
if (Test-Path -LiteralPath $archive) {
    Remove-Item -LiteralPath $archive -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($archive, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    $paths = @(".gitignore", "BASELINES.md", "connect_pi.ps1", "HEADLESS_FIRST_BOOT.md", "CONNECT_GUIDE.md", "install_pi.sh", "install_usb_offline.sh", "run_palm_demo.sh", "enable_ssh_remote.sh", "palm_demo.py", "palm_roi.py", "live_roi.py", "biometric.py", "roi_quality.py", "debug_ui.py", "palm-debug-ui.service", "PI5_SAFETY_CHECKLIST.md", "OFFLINE_RESOURCES.md", "README.md", "requirements-dev.txt", "models", "offline_wheels", "tools", "vendor", "windows")
    foreach ($path in $paths) {
        $item = Get-Item -LiteralPath (Join-Path $appRoot $path)
        $files = if ($item.PSIsContainer) { Get-ChildItem -LiteralPath $item.FullName -Recurse -File } else { @($item) }
        foreach ($file in $files) {
            $relative = $file.FullName.Substring($appRoot.Length + 1).Replace("\", "/")
            if ($relative -match '(^|/)(\.git|__pycache__|runtime|processed|dist)(/|$)') {
                continue
            }
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $relative) | Out-Null
        }
    }
}
finally {
    $zip.Dispose()
}
Write-Output $archive
