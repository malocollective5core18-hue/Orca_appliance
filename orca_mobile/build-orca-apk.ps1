$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$flutterRoot = 'C:\Users\RM ACCESSORIES\flutter'
$dart = Join-Path $flutterRoot 'bin\cache\dart-sdk\bin\dart.exe'
$flutterSnapshot = Join-Path $flutterRoot 'bin\cache\flutter_tools.snapshot'
$flutterPackages = Join-Path $flutterRoot 'packages\flutter_tools\.dart_tool\package_config.json'
$stage = Join-Path $env:TEMP ("orca-mobile-build-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))

foreach ($path in @($dart, $flutterSnapshot, $flutterPackages)) {
    if (-not (Test-Path $path)) {
        throw "Required Flutter SDK file not found: $path"
    }
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host 'Administrator PowerShell detected.'
} else {
    Write-Host 'Administrator access is not required; continuing with current permissions.'
}

$env:FLUTTER_ROOT = $flutterRoot
$env:ANDROID_HOME = 'C:\Android\Sdk'
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
if (-not (Test-Path $env:ANDROID_HOME)) {
    throw "Android SDK not found: $env:ANDROID_HOME"
}

New-Item -ItemType Directory -Path $stage -Force | Out-Null
foreach ($directory in @('lib', 'assets')) {
    Copy-Item -Path (Join-Path $projectRoot $directory) -Destination $stage -Recurse -Force
}
Copy-Item -Path (Join-Path $projectRoot 'pubspec.yaml') -Destination $stage -Force
if (Test-Path (Join-Path $projectRoot 'pubspec.lock')) {
    Copy-Item -Path (Join-Path $projectRoot 'pubspec.lock') -Destination $stage -Force
}

$androidSource = Join-Path $projectRoot 'android'
$androidDestination = Join-Path $stage 'android'
& robocopy $androidSource $androidDestination /E /XD .gradle build /NFL /NDL /NJH /NJS /NC /NS /NP
if ($LASTEXITCODE -ge 8) {
    throw "Could not stage Android project files (robocopy exit $LASTEXITCODE)."
}

Push-Location $stage
try {
    Write-Host 'Resolving Flutter dependencies...'
    & $dart "--packages=$flutterPackages" $flutterSnapshot pub get
    if ($LASTEXITCODE -ne 0) {
        throw "Flutter dependency resolution failed (exit $LASTEXITCODE). Staged files: $stage"
    }

    Write-Host 'Building debug APK...'
    Push-Location (Join-Path $stage 'android')
    try {
        & .\gradlew.bat --no-daemon --console=plain --stacktrace :app:assembleDebug
        if ($LASTEXITCODE -ne 0) {
            throw "Android APK build failed (exit $LASTEXITCODE). Staged files: $stage"
        }
    } finally {
        Pop-Location
    }
} finally {
    Pop-Location
}

$apk = Get-ChildItem -Path @((Join-Path $stage 'build'), (Join-Path $stage 'android\app\build')) `
    -Filter 'app-debug.apk' -File -Recurse -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $apk) {
    throw "Build reported success but app-debug.apk was not found. Staged files: $stage"
}

$destination = Join-Path $projectRoot 'orca-mobile-debug.apk'
Copy-Item -Path $apk.FullName -Destination $destination -Force
$builtApk = Get-Item $destination
$hash = Get-FileHash -Path $destination -Algorithm SHA256
Write-Host ''
Write-Host 'APK build completed.'
Write-Host "APK: $($builtApk.FullName)"
Write-Host "Size: $([math]::Round($builtApk.Length / 1MB, 2)) MB"
Write-Host "SHA256: $($hash.Hash)"
Write-Host "Staged build files: $stage"
