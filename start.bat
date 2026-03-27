@echo off
cd /d "%~dp0"

:: 启动 dailyhot-api（完全隐藏，不阻塞）
powershell -Command "Start-Process cmd -ArgumentList '/c cd dailyhot-api && npm run dev' -WindowStyle Hidden"

:: 启动 desktopWidgets（先激活虚拟环境，再用 pythonw 运行，完全隐藏）
powershell -Command "Start-Process cmd -ArgumentList '/c cd desktopWidgets && .venv\Scripts\activate && pythonw src\main.py' -WindowStyle Hidden"

exit