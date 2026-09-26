# PowerShell Script: Platform Comprehensive Health Check
$ErrorActionPreference = "Continue"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "HEALTHCARE DATA PLATFORM -- HEALTH CHECK" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Check PostgreSQL
$PgCheck = docker exec healthcare_postgres pg_isready -U healthcare
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] PostgreSQL:   $PgCheck" -ForegroundColor Green
} else {
    Write-Host "[FAIL] PostgreSQL is not responsive!" -ForegroundColor Red
}

# 2. Check Redis
$RedisCheck = docker exec healthcare_redis redis-cli ping
if ($RedisCheck -match "PONG") {
    Write-Host "[OK] Redis:        PONG" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Redis is not responsive!" -ForegroundColor Red
}

# 3. Check Airflow Containers
$AirflowContainers = docker ps --filter "name=healthcare_airflow" --format "{{.Names}}: {{.Status}}"
if ($AirflowContainers) {
    Write-Host "[OK] Airflow:      Running`n$AirflowContainers" -ForegroundColor Green
} else {
    Write-Host "[INFO] Airflow:    Containers not running locally (use start_airflow.ps1 if needed)" -ForegroundColor Yellow
}

Write-Host "==================================================" -ForegroundColor Cyan
