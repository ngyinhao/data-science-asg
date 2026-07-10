$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
$env:MPLCONFIGDIR = Join-Path $ProjectRoot "tmp\matplotlib"

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvSitePackages = Join-Path $ProjectRoot ".venv\Lib\site-packages"
$PythonExe = $VenvPython
$DependencyCheck = "import pandas, numpy, joblib, sklearn, streamlit"
$OriginalPythonPath = $env:PYTHONPATH

& $PythonExe -c $DependencyCheck *> $null
if ($LASTEXITCODE -ne 0) {
    $SystemPython = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $SystemPython) {
        throw "The virtual environment packages are not compatible with .venv Python, and no system Python fallback was found."
    }

    if ([string]::IsNullOrWhiteSpace($OriginalPythonPath)) {
        $env:PYTHONPATH = $VenvSitePackages
    }
    else {
        $env:PYTHONPATH = "$VenvSitePackages;$OriginalPythonPath"
    }

    & $SystemPython -c $DependencyCheck *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Python dependencies could not be imported. Recreate the virtual environment or reinstall requirements.txt."
    }

    $PythonExe = $SystemPython
}

& $PythonExe -m streamlit run "app\streamlit_app.py" --server.port 8501 --server.headless true --browser.gatherUsageStats false
