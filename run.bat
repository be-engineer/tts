@echo off
REM Edge TTS虚拟环境运行脚本 (Windows版本)
REM 自动检测、创建和激活虚拟环境

setlocal enabledelayedexpansion

REM 设置控制台为 UTF-8 编码
chcp 65001 >nul

cd /d "%~dp0"

echo ============================================================
echo Edge TTS - 虚拟环境管理器
echo ============================================================

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo [INFO] 未检测到虚拟环境,正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] 虚拟环境创建失败
        exit /b 1
    )
    echo [OK] 虚拟环境创建成功
) else (
    echo [OK] 检测到现有虚拟环境
)

REM 激活虚拟环境
echo [INFO] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
if exist "requirements.txt" (
    echo [INFO] 检查并安装基础依赖包...
    echo [INFO] 使用官方PyPI安装依赖...
    python -m pip install --upgrade pip -q --timeout 30
    pip install -r requirements.txt --timeout 60 --no-cache-dir
    if errorlevel 1 (
        echo [WARNING] 依赖安装失败,但将继续运行
        echo [INFO] 建议:
        echo    1. 检查网络连接
        echo    2. 尝试使用代理或VPN
        echo    3. 手动安装: venv\Scripts\activate ^&^& pip install -r requirements.txt
    ) else (
        echo [OK] 依赖安装完成
    )
) else (
    echo [WARNING] 未找到requirements.txt文件
)

echo.
echo ============================================================
echo 虚拟环境已激活
echo Python版本: 
python --version
echo ============================================================
echo.

REM 确定要运行的脚本
if "%~1"=="" (
    set SCRIPT_TO_RUN=edge_tts_gui_pyqt.py
) else (
    set SCRIPT_TO_RUN=%~1
)

REM 检查脚本是否存在
if not exist "%SCRIPT_TO_RUN%" (
    echo [ERROR] 脚本文件不存在: %SCRIPT_TO_RUN%
    call deactivate
    exit /b 1
)

echo [INFO] 正在运行: %SCRIPT_TO_RUN%
echo ============================================================

REM 设置Qt平台插件（确保文件对话框正常工作）
set QT_QPA_PLATFORM=windows

REM 运行脚本
python "%SCRIPT_TO_RUN%" %*
set EXIT_CODE=%errorlevel%

echo.
echo ============================================================
if %EXIT_CODE% equ 0 (
    echo [OK] 脚本执行成功
) else (
    echo [ERROR] 脚本执行失败 (退出码: %EXIT_CODE%)
)
echo ============================================================

REM 退出虚拟环境
call deactivate

exit /b %EXIT_CODE%