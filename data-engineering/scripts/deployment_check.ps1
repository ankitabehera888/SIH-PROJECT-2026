# PowerShell Script: Production Readiness Gate Check
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "PRODUCTION READINESS GATE CHECK" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$Checks = @()

# 1. PostgreSQL Connectivity
try {
    $PgCheck = docker exec healthcare_postgres pg_isready -U healthcare
    if ($LASTEXITCODE -eq 0) {
        $Checks += [PSCustomObject]@{ Service = "PostgreSQL"; Status = "PASS"; Details = "Connected" }
    } else {
        $Checks += [PSCustomObject]@{ Service = "PostgreSQL"; Status = "FAIL"; Details = "Connection Refused" }
    }
} catch {
    $Checks += [PSCustomObject]@{ Service = "PostgreSQL"; Status = "FAIL"; Details = $_.Exception.Message }
}

# 2. Redis Connectivity
try {
    $RedisCheck = docker exec healthcare_redis redis-cli ping
    if ($RedisCheck -match "PONG") {
        $Checks += [PSCustomObject]@{ Service = "Redis"; Status = "PASS"; Details = "PONG received" }
    } else {
        $Checks += [PSCustomObject]@{ Service = "Redis"; Status = "FAIL"; Details = "No response" }
    }
} catch {
    $Checks += [PSCustomObject]@{ Service = "Redis"; Status = "FAIL"; Details = $_.Exception.Message }
}

# 3. Required Analytics Schema & Tables
try {
    $TableCount = docker exec -i healthcare_postgres psql -U healthcare -d healthcare_dev -t -A -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'analytics' AND table_name IN ('dim_patient', 'fact_encounter', 'metric_results', 'quality_check_results', 'pipeline_runs');"
    $Cnt = [int]((-join $TableCount).Trim())
    if ($Cnt -eq 5) {
        $Checks += [PSCustomObject]@{ Service = "Analytics Schema"; Status = "PASS"; Details = "5/5 Core Tables Present" }
    } else {
        $Checks += [PSCustomObject]@{ Service = "Analytics Schema"; Status = "FAIL"; Details = "$Cnt/5 Tables Found" }
    }
} catch {
    $Checks += [PSCustomObject]@{ Service = "Analytics Schema"; Status = "FAIL"; Details = $_.Exception.Message }
}

# 4. Quality Gate State
try {
    $CriticalFailures = docker exec -i healthcare_postgres psql -U healthcare -d healthcare_dev -t -A -c "WITH latest AS (SELECT pipeline_run_id FROM analytics.quality_check_results ORDER BY execution_time DESC LIMIT 1) SELECT COUNT(*) FROM analytics.quality_check_results WHERE pipeline_run_id = (SELECT pipeline_run_id FROM latest) AND status IN ('FAIL', 'ERROR') AND severity = 'CRITICAL';"
    $Crits = [int]((-join $CriticalFailures).Trim())
    if ($Crits -eq 0) {
        $Checks += [PSCustomObject]@{ Service = "Quality Gate"; Status = "PASS"; Details = "0 Critical Failures" }
    } else {
        $Checks += [PSCustomObject]@{ Service = "Quality Gate"; Status = "FAIL"; Details = "$Crits Critical Failures Detected" }
    }
} catch {
    $Checks += [PSCustomObject]@{ Service = "Quality Gate"; Status = "WARNING"; Details = "No quality runs found yet" }
}

# Print Scorecard
$AllPassed = $true
foreach ($c in $Checks) {
    if ($c.Status -eq "PASS") {
        Write-Host ("{0,-20} {1,-8} ({2})" -f $c.Service, $c.Status, $c.Details) -ForegroundColor Green
    } else {
        Write-Host ("{0,-20} {1,-8} ({2})" -f $c.Service, $c.Status, $c.Details) -ForegroundColor Red
        $AllPassed = $false
    }
}

Write-Host "--------------------------------------------------" -ForegroundColor Cyan
if ($AllPassed) {
    Write-Host "RESULT: READY FOR PRODUCTION" -ForegroundColor Green
} else {
    Write-Host "RESULT: NOT READY (Resolve failing checks above)" -ForegroundColor Red
    exit 1
}
Write-Host "==================================================" -ForegroundColor Cyan
