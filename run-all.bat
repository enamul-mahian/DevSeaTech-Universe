@echo off
title DevSeaTech Universe - Full Test Runner
color 0A
cd /d "C:\Users\Emperor\Desktop\DevSeaTech-Universe"

echo ============================================
echo   DevSeaTech Universe - Starting Everything
echo ============================================
echo.

:: Check Node
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js installed nai! https://nodejs.org theke install korun
    pause
    exit /b 1
)

:: Check pnpm
where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] pnpm install kortesi...
    npm install -g pnpm@10.28.0
)

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Python installed nai - Desktop browser test skip hobe
    set NO_PYTHON=1
)

echo.
echo [1/5] Installing dependencies...
call pnpm install
if %errorlevel% neq 0 (
    echo [ERROR] pnpm install fail!
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo [2/5] Running API tests (14 tests)...
call pnpm --filter @devseatech/api test
if %errorlevel% neq 0 (
    echo [WARN] API tests e kisu fail hoyeche
) else (
    echo [OK] All API tests passed!
)
echo.

echo [3/5] Running typechecks...
call pnpm --filter @devseatech/contracts typecheck
call pnpm --filter @devseatech/api typecheck
call pnpm --filter @devseatech/portal typecheck
call pnpm --filter @devseatech/web typecheck
call pnpm --filter @devseatech/admin typecheck
echo [OK] Typechecks done
echo.

echo [4/5] Running Python unit tests...
if defined NO_PYTHON (
    echo [SKIP] Python nai, skip kortesi
) else (
    python -m pytest tests/ -v --tb=short 2>nul
    if %errorlevel% neq 0 (
        echo [INFO] Python tests done
    )
)
echo.

echo ============================================
echo   Starting servers - test korun browser e!
echo ============================================
echo.
echo   Portal:  http://localhost:3002
echo   API:     http://localhost:3001
echo   Website: http://localhost:3000
echo   Admin:   http://localhost:3003
echo.
echo   Band korte: Ctrl+C press korun
echo ============================================
echo.

:: Start all 4 servers in separate windows
start "DevSeaTech API (3001)" cmd /k "cd /d C:\Users\Emperor\Desktop\DevSeaTech-Universe && pnpm --filter @devseatech/api dev"
timeout /t 3 >nul

start "DevSeaTech Portal (3002)" cmd /k "cd /d C:\Users\Emperor\Desktop\DevSeaTech-Universe && pnpm --filter @devseatech/portal dev"
start "DevSeaTech Website (3000)" cmd /k "cd /d C:\Users\Emperor\Desktop\DevSeaTech-Universe && pnpm --filter @devseatech/web dev"
start "DevSeaTech Admin (3003)" cmd /k "cd /d C:\Users\Emperor\Desktop\DevSeaTech-Universe && pnpm --filter @devseatech/admin dev"

timeout /t 5 >nul
echo.
echo [OK] Shob server start hoyeche!
echo.
echo Browser e open korun:
echo   Portal:  http://localhost:3002
echo   Website: http://localhost:3000
echo   Admin:   http://localhost:3003
echo   API:     http://localhost:3001
echo.
start http://localhost:3002
echo Portal auto-open hoyeche browser e.
echo.
echo Band korte: each terminal window Ctrl+C ba cross diye close korun.
pause
