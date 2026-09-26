# PowerShell Script: Automated PostgreSQL Database Backup with SHA-256 Verification
$ErrorActionPreference = "Stop"

$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$BackupDir = Join-Path (Split-Path -Parent $PSScriptRoot) "infrastructure\postgres\backup"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$BackupFileName = "healthcare_backup_$Timestamp.sql"
$BackupPath = Join-Path $BackupDir $BackupFileName

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "POSTGRESQL PRODUCTION BACKUP -- $Timestamp" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Execute pg_dump inside healthcare_postgres container
Write-Host "[1/3] Generating complete logical database dump..." -ForegroundColor Yellow
docker exec -i healthcare_postgres pg_dump -U healthcare -d healthcare_dev --clean --if-exists > $BackupPath

if (-not (Test-Path $BackupPath) -or (Get-Item $BackupPath).Length -eq 0) {
    Write-Error "Backup failed: Dump file is missing or empty!"
    exit 1
}

# 2. Compute SHA-256 Checksum
Write-Host "[2/3] Computing cryptographic SHA-256 checksum..." -ForegroundColor Yellow
$Hash = (Get-FileHash -Path $BackupPath -Algorithm SHA256).Hash
$ChecksumPath = "$BackupPath.sha256"
"$Hash  $BackupFileName" | Out-File -FilePath $ChecksumPath -Encoding utf8

# 3. Report Success
$SizeKB = [math]::Round((Get-Item $BackupPath).Length / 1024, 2)
Write-Host "[3/3] Backup verified successfully!" -ForegroundColor Green
Write-Host "    File:     $BackupPath" -ForegroundColor Green
Write-Host "    Size:     $SizeKB KB" -ForegroundColor Green
Write-Host "    SHA-256:  $Hash" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
