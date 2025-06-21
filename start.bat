@echo off
echo ========================================
echo    视频质量分析器启动脚本
echo ========================================
echo.

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo 正在启动视频质量分析器...
echo 服务将在 http://localhost:8000 启动
echo 按 Ctrl+C 停止服务
echo.

python main.py

pause 