# PowerShell script to test webhook on Windows
# Run this with: .\test_webhook_windows.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Testing Webhook Server" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan

# Test 1: Check if server is running
Write-Host "`nTest 1: Checking server status..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Server is running!" -ForegroundColor Green
    Write-Host "   Status: $($data.status)" -ForegroundColor White
    Write-Host "   Analyses completed: $($data.analyses_completed)" -ForegroundColor White
} catch {
    Write-Host "❌ Server is not running!" -ForegroundColor Red
    Write-Host "   Start it with: python webhook_server.py" -ForegroundColor Yellow
    exit 1
}

# Test 2: Trigger analysis
Write-Host "`nTest 2: Triggering analysis..." -ForegroundColor Cyan
$repoUrl = "https://github.com/Kaushik-SPACEZ/github-agent"
Write-Host "   Repository: $repoUrl" -ForegroundColor White

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/analyze?repo_url=$repoUrl" -Method POST
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Analysis triggered!" -ForegroundColor Green
    Write-Host "   Status: $($data.status)" -ForegroundColor White
    Write-Host "   Message: $($data.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to trigger analysis!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 3: Check history
Write-Host "`nTest 3: Checking analysis history..." -ForegroundColor Cyan
Start-Sleep -Seconds 2  # Wait for analysis to start

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/history" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ History retrieved!" -ForegroundColor Green
    Write-Host "   Total analyses: $($data.total)" -ForegroundColor White
    
    if ($data.analyses.Count -gt 0) {
        Write-Host "`n   Recent analyses:" -ForegroundColor White
        foreach ($analysis in $data.analyses | Select-Object -Last 3) {
            $time = [DateTime]::Parse($analysis.timestamp).ToString("HH:mm:ss")
            $status = if ($analysis.success) { "✅" } else { "❌" }
            Write-Host "   $status $time - $($analysis.repo_url)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "❌ Failed to get history!" -ForegroundColor Red
}

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Test Complete!" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan

Write-Host "`n📊 Open dashboard.html to see results visually!" -ForegroundColor Green
Write-Host "🔄 The analysis is running in the background..." -ForegroundColor Yellow