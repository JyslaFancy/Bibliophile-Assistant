# Bibliophile Assistant — Windows Installer
# One-liner: irm https://raw.githubusercontent.com/JyslaFancy/Bibliophile-Assistant/main/install.ps1 | iex
#
# Downloads the latest bibliophile.exe, places it in a sensible location,
# and adds it to your user PATH so 'bibliophile' works from any terminal.

param(
    [string]$Version = "",
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\Bibliophile"
)

# Allow setting version via environment variable for one-liner pipe usage
if (-not $Version -and $env:BIBLIOPHILE_VERSION) {
    $Version = $env:BIBLIOPHILE_VERSION
}
if (-not $Version) {
    $Version = "latest"
}

$ErrorActionPreference = "Stop"
$Repo = "JyslaFancy/Bibliophile-Assistant"

Write-Host ""
Write-Host "    Bibliophile Assistant Installer" -ForegroundColor Cyan
Write-Host "    ===============================" -ForegroundColor Cyan
Write-Host ""

# --- Determine download URL ---
if ($Version -eq "latest") {
    Write-Host "  Finding latest release..." -ForegroundColor Gray
    try {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
        $tag = $release.tag_name
        $versionClean = $tag -replace '^v', ''
    } catch {
        Write-Host "  ERROR: Could not find latest release. Try specifying a version:" -ForegroundColor Red
        Write-Host "    irm .../install.ps1 | iex -Version v0.1.1" -ForegroundColor Red
        exit 1
    }
} else {
    $tag = $Version -replace '^v', ''
    $tag = "v$tag"
    $versionClean = $Version -replace '^v', ''
}

$url = "https://github.com/$Repo/releases/download/$tag/bibliophile.exe"
Write-Host "  Version: $tag" -ForegroundColor White
Write-Host "  Download: $url" -ForegroundColor Gray

# --- Download ---
Write-Host "  Downloading..." -ForegroundColor Gray
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$exePath = Join-Path $InstallDir "bibliophile.exe"

try {
    Invoke-WebRequest -Uri $url -OutFile $exePath -UseBasicParsing
} catch {
    Write-Host "  ERROR: Download failed. Is the release published?" -ForegroundColor Red
    Write-Host "  URL: $url" -ForegroundColor Red
    exit 1
}

$sizeMB = [math]::Round((Get-Item $exePath).Length / 1MB, 1)
Write-Host "  Downloaded: $exePath ($sizeMB MB)" -ForegroundColor Green

# --- Add to PATH ---
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$InstallDir*") {
    Write-Host "  Adding to user PATH..." -ForegroundColor Gray
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$InstallDir", "User")
    # Update current session too
    $env:Path = "$env:Path;$InstallDir"
    Write-Host "  Added $InstallDir to PATH" -ForegroundColor Green
    Write-Host ""
    Write-Host "  IMPORTANT: Restart your terminal for PATH to take effect," -ForegroundColor Yellow
    Write-Host "  or run this in the current session:" -ForegroundColor Yellow
    Write-Host "    `$env:Path += ';$InstallDir'" -ForegroundColor White
} else {
    Write-Host "  Already in PATH." -ForegroundColor Gray
}

Write-Host ""
Write-Host "  DONE! Run 'bibliophile setup' to get started." -ForegroundColor Green
Write-Host ""
