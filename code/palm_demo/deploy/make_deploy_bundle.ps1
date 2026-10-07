$appRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$outputDir = Join-Path $appRoot "dist"
$archive = Join-Path $outputDir "palm_demo_pi.zip"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
if (Test-Path -LiteralPath $archive) {
    Remove-Item -LiteralPath $archive -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($archive, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    $paths = @(".gitignore", "docs", "deploy", "palm_app", "debug_ui.py", "README.md", "requirements-dev.txt", "models", "tools", "vendor")
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
