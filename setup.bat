@echo off
chcp 65001 >nul

cd /d "%~dp0"

echo ==========================================
echo DailyAPI 环境配置脚本
echo ==========================================
echo.

:: 检测 Node.js 和 npm
echo [1/5] 检测 Node.js 环境...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 16+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo Node.js 版本: %NODE_VERSION%

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 npm，请确认 Node.js 安装完整
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i
echo npm 版本: %NPM_VERSION%
echo.

:: 检测 Python
echo [2/5] 检测 Python 环境...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python 版本: %PYTHON_VERSION%
echo.

:: 检测 Git (可选，用于克隆仓库)
echo [3/5] 检测 Git 环境...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [警告] 未检测到 Git，将无法自动克隆仓库
    echo 请手动将 dailyhot-api 项目克隆到当前目录下的 dailyhot-api 文件夹中
    echo 仓库地址: https://github.com/kuole-o/dailyhot-api
    echo.
    pause
    if not exist "dailyhot-api" (
        echo [错误] 未找到 dailyhot-api 目录，请手动克隆后重新运行脚本
        pause
        exit /b 1
    )
) else (
    echo Git 已安装
    if not exist "dailyhot-api" (
        echo 正在克隆 dailyhot-api 仓库...
        git clone https://github.com/kuole-o/dailyhot-api.git dailyhot-api
        if %errorlevel% neq 0 (
            echo [错误] 克隆失败，请检查网络后重试
            pause
            exit /b 1
        )
        echo 克隆完成
    ) else (
        echo dailyhot-api 目录已存在，跳过克隆
    )
)
echo.

:: 安装 Node.js 依赖
echo [4/5] 安装 dailyhot-api 依赖...
cd dailyhot-api
if exist "package.json" (
    echo 正在运行 npm install...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] npm install 失败
        cd ..
        pause
        exit /b 1
    )
    echo Node.js 依赖安装完成
) else (
    echo [错误] dailyhot-api 目录下未找到 package.json，请检查目录结构
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ==========================================
echo Node.js 依赖安装已完成
echo.
echo 按任意键继续安装 Python 依赖...
echo ==========================================
pause >nul
echo.

:: 安装 Python 依赖
echo [5/5] 安装 desktopWidgets 依赖...
cd desktopWidgets
if not exist ".venv" (
    echo 创建 Python 虚拟环境...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败
        cd ..
        pause
        exit /b 1
    )
)
echo 激活虚拟环境...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [错误] 激活虚拟环境失败
    cd ..
    pause
    exit /b 1
)
echo 安装 requirements.txt 中的依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 安装 Python 依赖失败
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ==========================================
echo 所有依赖安装完成！
echo.
echo 现在可以使用 start.bat 启动应用
echo ==========================================
pause