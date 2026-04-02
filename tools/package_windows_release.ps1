param(
    [ValidateSet("all", "onedir", "onefile")]
    [string]$Mode = "all",
    [string]$Python = "python",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $projectRoot "packaging\package_release.ps1") -Mode $Mode -Python $Python -SkipBuild:$SkipBuild
