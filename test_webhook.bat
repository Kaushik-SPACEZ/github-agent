@echo off
echo ======================================================================
echo Testing Webhook Server
echo ======================================================================
echo.

echo Test 1: Checking server status...
curl http://localhost:8000/
echo.
echo.

echo Test 2: Triggering analysis...
curl -X POST http://localhost:8000/analyze?repo_url=https://github.com/Kaushik-SPACEZ/github-agent
echo.
echo.

echo Test 3: Checking history...
timeout /t 2 /nobreak >nul
curl http://localhost:8000/history
echo.
echo.

echo ======================================================================
echo Test Complete!
echo ======================================================================
echo.
echo Open dashboard.html to see results visually!
echo.
pause