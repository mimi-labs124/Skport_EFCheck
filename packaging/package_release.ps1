param(
    [ValidateSet("all", "onedir", "onefile")]
    [string]$Mode = "all",
    [string]$Python = "python",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

function Invoke-ReleaseZip {
    param(
        [string]$SelectedMode
    )

    $env:EFCHECK_PROJECT_ROOT = $projectRoot
    @"
import os
from pathlib import Path
from efcheck.packaging.pyinstaller_helpers import create_release_zip

project_root = Path(os.environ["EFCHECK_PROJECT_ROOT"])
zip_path = create_release_zip("$SelectedMode", project_root)
print(zip_path)
"@ | & $Python -
}

Push-Location $projectRoot
try {
    $selectedModes = @()
    if ($Mode -eq "all") {
        $selectedModes = @("onedir", "onefile")
    } else {
        $selectedModes = @($Mode)
    }

    if (-not $SkipBuild) {
        foreach ($selectedMode in $selectedModes) {
            if ($selectedMode -eq "onedir") {
                & (Join-Path $PSScriptRoot "build_onedir.ps1") -Python $Python
            } elseif ($selectedMode -eq "onefile") {
                & (Join-Path $PSScriptRoot "build_onefile.ps1") -Python $Python
            }
        }
    }

    foreach ($selectedMode in $selectedModes) {
        Invoke-ReleaseZip -SelectedMode $selectedMode
    }
}
finally {
    Pop-Location
}
