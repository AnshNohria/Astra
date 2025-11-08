# 🧪 System Verification Script
# Run this to verify your environment is ready for the demo

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   ASTRA - Environment Verification" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$allGood = $true

# Check Python
Write-Host "🐍 Checking Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Python not found!" -ForegroundColor Red
    $allGood = $false
}

# Check Docker
Write-Host "`n🐳 Checking Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerVersion = docker --version
    Write-Host "   ✓ $dockerVersion" -ForegroundColor Green
    
    # Check if Docker daemon is running
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Docker daemon is running" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Docker daemon is not running!" -ForegroundColor Red
        Write-Host "     Please start Docker Desktop" -ForegroundColor Yellow
        $allGood = $false
    }
} else {
    Write-Host "   ✗ Docker not found!" -ForegroundColor Red
    $allGood = $false
}

# Check pip packages
Write-Host "`n📦 Checking Python packages..." -ForegroundColor Yellow
$requiredPackages = @("boto3", "moto", "kafka-python", "click")
foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>&1 | Select-String "Name:"
    if ($installed) {
        Write-Host "   ✓ $package installed" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $package not installed" -ForegroundColor Red
        $allGood = $false
    }
}

# Check if docker-compose.yml exists
Write-Host "`n📄 Checking project files..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    Write-Host "   ✓ docker-compose.yml found" -ForegroundColor Green
} else {
    Write-Host "   ✗ docker-compose.yml not found!" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path "main.py") {
    Write-Host "   ✓ main.py found" -ForegroundColor Green
} else {
    Write-Host "   ✗ main.py not found!" -ForegroundColor Red
    $allGood = $false
}

# Final verdict
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✓ All checks passed! Ready to demo!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: docker-compose up -d" -ForegroundColor White
    Write-Host "  2. Wait 20 seconds for Kafka to start" -ForegroundColor White
    Write-Host "  3. Run: python main.py check-kafka" -ForegroundColor White
    Write-Host "  4. Follow DEMO_GUIDE.md for the full demo`n" -ForegroundColor White
} else {
    Write-Host "✗ Some checks failed. Please fix the issues above." -ForegroundColor Red
    Write-Host "`nQuick fixes:" -ForegroundColor Cyan
    Write-Host "  • Install packages: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "  • Start Docker: Open Docker Desktop`n" -ForegroundColor White
}
Write-Host "========================================`n" -ForegroundColor Cyan
