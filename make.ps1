# make.ps1 — equivalente del Makefile para Windows, donde no hay `make`.
#
# Ejecuta exactamente los mismos comandos que el Makefile, para que lo que pasa
# aquí sea lo mismo que pasa en CI. Si los dos ficheros dejan de coincidir,
# manda el Makefile: es el que ejecuta CI.
#
#   .\make.ps1 verify

param([Parameter(Position = 0)][string]$Target = "help")

$ErrorActionPreference = "Stop"

if (Test-Path ".venv\Scripts\python.exe") {
    $py = ".venv\Scripts\python.exe"
} else {
    $py = "python"
}

function Invoke-Step {
    param([string]$Titulo, [string[]]$Comando)

    Write-Host ""
    Write-Host "== $Titulo" -ForegroundColor Cyan
    & $py @Comando
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "FALLO en: $Titulo" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

function Step-Lint {
    Invoke-Step "ruff check" @("-m", "ruff", "check", "src", "tests")
    Invoke-Step "ruff format --check" @("-m", "ruff", "format", "--check", "src", "tests")
}
function Step-Typecheck { Invoke-Step "mypy" @("-m", "mypy") }
function Step-Test      { Invoke-Step "pytest" @("-m", "pytest", "-m", "not smoke") }
function Step-Smoke     { Invoke-Step "pytest (humo)" @("-m", "pytest", "-m", "smoke") }

switch ($Target) {
    "help" {
        Write-Host "setup      crea .venv e instala el proyecto con sus dependencias de desarrollo"
        Write-Host "verify     lint + typecheck + tests + humo. El unico juez"
        Write-Host "lint       ruff: reglas y formato"
        Write-Host "format     ruff format: reformatea el codigo"
        Write-Host "typecheck  mypy en modo estricto"
        Write-Host "test       tests unitarios (sin el de humo)"
        Write-Host "smoke      test de humo: backtest corto sobre fixtures"
        Write-Host "report     informe HTML completo             [pendiente, M7]"
        Write-Host "run-day    un dia de paper trading           [pendiente, M8]"
        Write-Host "dashboard  dashboard web estatico            [pendiente, M9]"
        Write-Host "clean      borra caches y artefactos de build"
    }
    "setup" {
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & ".venv\Scripts\python.exe" -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & ".venv\Scripts\python.exe" -m pip install -e ".[dev]"
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host ""
        Write-Host "Listo. Ejecuta: .\make.ps1 verify"
    }
    "verify" {
        Step-Lint
        Step-Typecheck
        Step-Test
        Step-Smoke
        Write-Host ""
        Write-Host "verify OK" -ForegroundColor Green
    }
    "lint"      { Step-Lint }
    "typecheck" { Step-Typecheck }
    "test"      { Step-Test }
    "smoke"     { Step-Smoke }
    "format" {
        Invoke-Step "ruff format" @("-m", "ruff", "format", "src", "tests")
        Invoke-Step "ruff check --fix" @("-m", "ruff", "check", "--fix", "src", "tests")
    }
    "report"    { & $py -m momentum.cli report;    exit $LASTEXITCODE }
    "run-day"   { & $py -m momentum.cli run-day;   exit $LASTEXITCODE }
    "dashboard" { & $py -m momentum.cli dashboard; exit $LASTEXITCODE }
    "clean" {
        foreach ($dir in @(".mypy_cache", ".ruff_cache", ".pytest_cache", "build", "dist")) {
            if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
        }
        Get-ChildItem -Recurse -Directory -Filter "__pycache__" |
            ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
        Write-Host "Limpio."
    }
    default {
        Write-Host "Objetivo desconocido: $Target" -ForegroundColor Red
        Write-Host "Ejecuta .\make.ps1 help para ver los disponibles."
        exit 2
    }
}
