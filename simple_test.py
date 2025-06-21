#!/usr/bin/env python3
"""
简单的功能测试脚本
"""

import os
import sys
import requests
import time

def test_server():
    """测试服务器是否运行"""
    print("🌐 测试服务器连接...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {str(e)}")
        return False

def test_main_page():
    """测试主页面"""
    print("\n📄 测试主页面...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 主页面可访问")
            return True
        else:
            print(f"❌ 主页面异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法访问主页面: {str(e)}")
        return False

def test_api_health():
    """测试API健康检查"""
    print("\n🏥 测试API健康检查...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API健康检查通过: {data}")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API健康检查异常: {str(e)}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🔗 测试API端点...")
    try:
        # 测试API路由前缀
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code == 404:  # 这是预期的，因为没有根API端点
            print("✅ API路由配置正确")
            return True
        else:
            print(f"❌ API路由异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API端点测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 简单功能测试")
    print("=" * 30)
    
    tests = [
        ("服务器连接", test_server),
        ("主页面", test_main_page),
        ("API健康检查", test_api_health),
        ("API端点", test_api_endpoints)
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
    
    print("\n" + "=" * 30)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 基本功能测试通过！")
        print("\n🌐 访问地址:")
        print("主页: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("健康检查: http://localhost:8000/health")
    else:
        print("⚠️  部分测试失败，请检查服务器状态。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 