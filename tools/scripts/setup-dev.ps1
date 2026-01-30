# Development Environment Setup
# Run this script to set up your local development environment

param(
    [switch]$SkipDocker,
    [switch]$SkipPython
)

$ErrorActionPreference = "Stop"

Write-Host "Setting up WaqediAI development environment..." -ForegroundColor Green

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

# Python
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[1-9]") {
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  Python 3.11+ required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Docker
if (-not $SkipDocker) {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Docker: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "  Docker not found. Install Docker Desktop or use -SkipDocker" -ForegroundColor Yellow
    }
}

# Create virtual environment
if (-not $SkipPython) {
    Write-Host "`nCreating Python virtual environment..." -ForegroundColor Yellow

    if (-not (Test-Path ".venv")) {
        python -m venv .venv
    }

    # Activate virtual environment
    & .\.venv\Scripts\Activate.ps1

    # Upgrade pip
    python -m pip install --upgrade pip

    # Install shared libraries
    Write-Host "`nInstalling shared libraries..." -ForegroundColor Yellow
    pip install -e libs/common
    pip install -e libs/observability

    # Install development tools
    Write-Host "`nInstalling development tools..." -ForegroundColor Yellow
    pip install black ruff mypy pytest pytest-cov pre-commit
}

# Copy environment template
if (-not (Test-Path ".env")) {
    Write-Host "`nCreating .env from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Start Docker services
if (-not $SkipDocker) {
    Write-Host "`nStarting Docker services..." -ForegroundColor Yellow
    docker-compose up -d
}

# Setup pre-commit hooks
Write-Host "`nSetting up pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

Write-Host "`n Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Activate venv: .\.venv\Scripts\Activate.ps1"
Write-Host "  2. Start a service: cd services/query-orchestrator && make dev"
Write-Host "  3. View services: docker-compose ps"
