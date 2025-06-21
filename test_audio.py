#!/usr/bin/env python3
"""
音频分析功能测试脚本
"""

import os
import sys
import requests
import time
import json

def test_audio_analysis():
    """测试音频分析功能"""
    print("🎵 测试音频分析功能...")
    
    # 检查是否有测试视频文件
    test_video = None
    for file in os.listdir("uploads"):
        if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            test_video = os.path.join("uploads", file)
            break
    
    if not test_video:
        print("❌ 未找到测试视频文件，请先上传一个视频文件")
        return False
    
    print(f"📹 使用测试视频: {test_video}")
    
    # 1. 上传视频
    print("\n📤 上传视频...")
    with open(test_video, 'rb') as f:
        files = {'file': (os.path.basename(test_video), f, 'video/mp4')}
        response = requests.post('http://localhost:8000/api/upload-video', files=files)
    
    if response.status_code != 200:
        print(f"❌ 上传失败: {response.status_code}")
        return False
    
    upload_result = response.json()
    file_path = upload_result['file_path']
    print(f"✅ 上传成功: {file_path}")
    
    # 2. 开始分析
    print("\n🔍 开始视频分析...")
    analysis_request = {
        "video_file": file_path,
        "video_url": None
    }
    
    response = requests.post('http://localhost:8000/api/analyze-video', json=analysis_request)
    if response.status_code != 200:
        print(f"❌ 启动分析失败: {response.status_code}")
        return False
    
    analysis_result = response.json()
    task_id = analysis_result['task_id']
    print(f"✅ 分析任务已启动: {task_id}")
    
    # 3. 监控进度
    print("\n⏳ 监控分析进度...")
    while True:
        response = requests.get(f'http://localhost:8000/api/analysis-progress/{task_id}')
        if response.status_code != 200:
            print(f"❌ 获取进度失败: {response.status_code}")
            return False
        
        progress = response.json()
        print(f"进度: {progress['progress']:.1f}% - {progress['message']}")
        
        if progress['status'] == 'completed':
            print("✅ 分析完成！")
            break
        elif progress['status'] == 'failed':
            print(f"❌ 分析失败: {progress['message']}")
            return False
        
        time.sleep(2)
    
    # 4. 获取结果
    print("\n📊 获取分析结果...")
    response = requests.get(f'http://localhost:8000/api/analysis-result/{task_id}')
    if response.status_code != 200:
        print(f"❌ 获取结果失败: {response.status_code}")
        return False
    
    result = response.json()
    
    # 5. 检查音频分析结果
    print("\n🎵 检查音频分析结果...")
    audio_analysis = result.get('audio_analysis', {})
    
    if audio_analysis.get('success', False):
        print("✅ 音频分析成功")
        
        transcription = audio_analysis.get('transcription', {})
        audio_quality = audio_analysis.get('audio_quality', {})
        
        print(f"📝 转录文本长度: {len(transcription.get('text', ''))} 字符")
        print(f"🎚️ 音频质量评分: {audio_quality.get('quality_score', 0):.1f}/100")
        print(f"⏱️ 音频时长: {audio_quality.get('duration', 0):.2f} 秒")
        print(f"🔊 采样率: {audio_quality.get('sample_rate', 0)} Hz")
        print(f"🎧 声道数: {audio_quality.get('channels', 0)}")
        
        if transcription.get('text'):
            print(f"\n📄 转录内容预览:")
            text = transcription.get('text', '')
            print(text[:200] + "..." if len(text) > 200 else text)
        
        # 检查摘要中的音频信息
        summary = result.get('summary', {})
        print(f"\n📈 摘要中的音频信息:")
        print(f"   音频质量评分: {summary.get('audio_quality_score', 0):.1f}/100")
        print(f"   音频转录状态: {'有转录' if summary.get('has_audio_transcription', False) else '无转录'}")
        
    else:
        print(f"❌ 音频分析失败: {audio_analysis.get('error', '未知错误')}")
    
    # 6. 下载报告
    print("\n📄 下载分析报告...")
    for format_type in ['json', 'pdf', 'excel']:
        try:
            response = requests.get(f'http://localhost:8000/api/download-report/{task_id}?format={format_type}')
            if response.status_code == 200:
                filename = f"test_audio_report.{format_type}"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ {format_type.upper()} 报告已下载: {filename}")
            else:
                print(f"❌ 下载 {format_type} 报告失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 下载 {format_type} 报告异常: {str(e)}")
    
    print("\n🎉 音频分析功能测试完成！")
    return True

if __name__ == "__main__":
    try:
        success = test_audio_analysis()
        if success:
            print("\n✅ 所有测试通过！")
        else:
            print("\n❌ 测试失败！")
    except Exception as e:
        print(f"\n💥 测试异常: {str(e)}")
        import traceback
        traceback.print_exc() 