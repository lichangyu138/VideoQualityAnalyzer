#!/usr/bin/env python3
"""
视频质量分析器系统测试脚本
"""

import os
import sys
import logging
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def test_environment():
    """测试环境配置"""
    print("🔍 测试环境配置...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要目录
    Config.create_directories()
    required_dirs = ['uploads', 'outputs', 'temp_frames', 'downloads']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录不存在: {dir_name}")
            return False
    
    return True

def test_dependencies():
    """测试依赖包"""
    print("\n📦 测试依赖包...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'opencv-python',
        'torch',
        'ultralytics',
        'transformers',
        'easyocr',
        'pandas',
        'reportlab',
        'yt-dlp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def test_models():
    """测试模型加载"""
    print("\n🤖 测试模型加载...")
    
    try:
        # 测试YOLO模型
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✅ YOLOv8 模型加载成功")
        
        # 测试CLIP模型
        from transformers import CLIPProcessor, CLIPModel
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        print("✅ CLIP 模型加载成功")
        
        # 测试OCR
        import easyocr
        reader = easyocr.Reader(['ch_sim', 'en'])
        print("✅ OCR 模型加载成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型加载失败: {str(e)}")
        return False

def test_api():
    """测试API服务"""
    print("\n🌐 测试API服务...")
    
    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # 创建测试应用
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        # 测试客户端
        client = TestClient(app)
        response = client.get("/test")
        
        if response.status_code == 200:
            print("✅ API服务测试成功")
            return True
        else:
            print("❌ API服务测试失败")
            return False
            
    except Exception as e:
        print(f"❌ API服务测试失败: {str(e)}")
        return False

def test_video_processing():
    """测试视频处理功能"""
    print("\n🎬 测试视频处理功能...")
    
    try:
        import cv2
        import numpy as np
        
        # 创建一个测试视频
        test_video_path = "test_video.mp4"
        
        # 创建测试帧
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :, 0] = 255  # 蓝色背景
        
        # 写入测试视频
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(test_video_path, fourcc, 30.0, (640, 480))
        
        for _ in range(30):  # 1秒视频
            out.write(frame)
        
        out.release()
        
        # 测试读取视频
        cap = cv2.VideoCapture(test_video_path)
        if cap.isOpened():
            print("✅ 视频处理功能正常")
            cap.release()
            
            # 清理测试文件
            if os.path.exists(test_video_path):
                os.remove(test_video_path)
            
            return True
        else:
            print("❌ 视频处理功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 视频处理测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 视频质量分析器系统测试")
    print("=" * 50)
    
    tests = [
        ("环境配置", test_environment),
        ("依赖包", test_dependencies),
        ("模型加载", test_models),
        ("API服务", test_api),
        ("视频处理", test_video_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name}测试失败")
        except Exception as e:
            print(f"❌ {test_name}测试异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        print("\n启动命令:")
        print("python main.py")
        print("或双击 start.bat")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 