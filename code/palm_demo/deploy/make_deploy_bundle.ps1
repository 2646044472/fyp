param([switch]$IncludePKLNet)
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
    $paths = @(".gitignore", "docs", "deploy", "palm_app", "debug_ui.py", "palmir_page.py", "pklnet_roi.py", "pklnet_policy.py", "pklnet_tracker.py", "pose_matcher.py", "registered_matcher.py", "multiroi_matcher.py", "union_matcher.py", "window_roi.py", "roi_sampling.py", "capture_page.py", "collection_page.py", "demo_flow.py", "demo_page.py", "gallery.py", "payment.py", "templates.py", "models.py", "biometric.py", "palm_roi.py", "roi_quality.py", "live_roi.py", "README.md", "requirements-dev.txt", "requirements-pklnet.txt", "models", "tools", "vendor")
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
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, (Join-Path $appRoot "requirements-palmir.txt"), "requirements-palmir.txt") | Out-Null
    $pklnetRoot = Join-Path (Split-Path -Parent $appRoot) "pklnet"
    foreach ($path in $(if ($IncludePKLNet) { @("lib", "roiExtractor.py", "net_params_500.pth", "README.md") } else { @() })) {
        $item = Get-Item -LiteralPath (Join-Path $pklnetRoot $path)
        $files = if ($item.PSIsContainer) { Get-ChildItem -LiteralPath $item.FullName -Recurse -File } else { @($item) }
        foreach ($file in $files) {
            $relative = $file.FullName.Substring($pklnetRoot.Length + 1).Replace("\", "/")
            if ($relative -match '(^|/)(__pycache__|\.git)(/|$)' -or $relative -match '\.(pyc|obj)$') { continue }
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, "pklnet/$relative") | Out-Null
        }
    }
    if ($IncludePKLNet) {
        foreach ($name in @("pklnet-keypoints.onnx", "pklnet-keypoints.json", "pklnet-keypoints-diagnostics.onnx", "pklnet-keypoints-diagnostics.json")) {
            $modelPath = Join-Path $pklnetRoot $name
            if (Test-Path -LiteralPath $modelPath) {
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $modelPath, "pklnet/$name") | Out-Null
            }
        }
    }
}
finally {
    $zip.Dispose()
}
Write-Output $archive
