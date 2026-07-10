[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

function Find-Python312 {
    $candidates = @(
        @{ Command = "py"; Args = @("-3.12") },
        @{ Command = "python3.12"; Args = @() },
        @{ Command = "python"; Args = @() }
    )

    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Command -ErrorAction SilentlyContinue
        if (-not $command) {
            continue
        }

        $checkArgs = @($candidate.Args) + @(
            "-c",
            "import sys; print(sys.executable); print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
        )

        try {
            $output = & $command.Source @checkArgs 2>$null
            if ($LASTEXITCODE -ne 0 -or $output.Count -lt 2) {
                continue
            }

            if ($output[1] -like "3.12.*") {
                return @{
                    Command = $command.Source
                    Args = $candidate.Args
                    Executable = $output[0]
                    Version = $output[1]
                }
            }
        }
        catch {
            continue
        }
    }

    throw "Python 3.12 was not found. Install Python 3.12 first, then run this script again."
}

function Invoke-SelectedPython {
    param(
        [hashtable]$Python,
        [string[]]$Arguments
    )

    $allArgs = @($Python.Args) + $Arguments
    & $Python.Command @allArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Python.Command) $($allArgs -join ' ')"
    }
}

$python312 = Find-Python312
Write-Host "Using Python $($python312.Version): $($python312.Executable)"

if (-not (Test-Path $RequirementsPath)) {
    throw "Cannot find requirements.txt at $RequirementsPath"
}

if (Test-Path $VenvPath) {
    $resolvedVenv = (Resolve-Path $VenvPath).Path
    $expectedVenv = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot ".venv"))

    if ($resolvedVenv -ne $expectedVenv) {
        throw "Refusing to remove unexpected virtual environment path: $resolvedVenv"
    }

    if (-not $Force) {
        $answer = Read-Host "This will delete and rebuild $resolvedVenv. Type YES to continue"
        if ($answer -ne "YES") {
            Write-Host "Cancelled. Existing .venv was not changed."
            exit 0
        }
    }

    Remove-Item -LiteralPath $resolvedVenv -Recurse -Force
}

Invoke-SelectedPython -Python $python312 -Arguments @("-m", "venv", $VenvPath)

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
& $VenvPython --version
if ($LASTEXITCODE -ne 0) {
    throw "The new virtual environment Python could not be started."
}

& $VenvPython -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)"
if ($LASTEXITCODE -ne 0) {
    throw "The new virtual environment is not using Python 3.12."
}

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

if (-not $SkipInstall) {
    & $VenvPython -m pip install -r $RequirementsPath
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install requirements.txt."
    }

    & $VenvPython -c "import pandas, numpy, joblib, sklearn, streamlit; print('Dependency check passed.')"
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency check failed after installation."
    }
}

Write-Host ""
Write-Host "Done. Activate the environment with:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
