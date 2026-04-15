@echo off
REM 开发工具快捷脚本 (Windows)
REM Usage: scripts\dev.bat [command]

setlocal enabledelayedexpansion

cd /d "%~dp0.."

if "%1"=="" goto :usage
if "%1"=="format" goto :format
if "%1"=="check" goto :check
if "%1"=="test" goto :test
if "%1"=="serve" goto :serve
goto :usage

:format
echo 运行代码格式化...
python scripts\format.py
goto :end

:check
echo 运行质量检查...
python scripts\check_quality.py
goto :end

:test
echo 运行测试...
cd backend && uv run pytest -v
goto :end

:serve
echo 启动开发服务器...
cd backend && uv run uvicorn app:app --reload --port 8000
goto :end

:usage
echo 开发工具快捷脚本
echo.
echo 用法: scripts\dev.bat [command]
echo.
echo 可用命令:
echo   format  - 格式化所有代码
echo   check   - 运行代码质量检查
echo   test    - 运行测试套件
echo   serve   - 启动开发服务器
echo.

:end
endlocal
