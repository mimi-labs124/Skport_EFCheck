param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $projectRoot
try {
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -e ".[dev]"
    & $Python -m efcheck package onefile
}
finally {
    Pop-Location
}
