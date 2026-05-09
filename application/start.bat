@echo off
chcp 65001 >nul
echo ========================================
echo    无人机监控系统启动脚本
echo ========================================
echo.

REM 检查是否激活了YOLO-GPU环境
echo 正在检查conda环境...
conda activate YOLO-GPU

echo.
echo 启动Flask应用...
cd /d "%~dp0"
python app.py

pause