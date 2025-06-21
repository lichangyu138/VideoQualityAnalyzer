from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import asyncio
from typing import Optional
import logging

from ..models.schemas import VideoAnalysisRequest, AnalysisProgress, ErrorResponse
from ..services.video_processor import VideoProcessor
from ..services.image_analyzer import ImageAnalyzer
from ..utils.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局变量存储分析任务状态
analysis_tasks = {}

@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """上传视频文件"""
    try:
        # 检查文件类型
        if not file.filename or not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv')):
            raise HTTPException(status_code=400, detail="不支持的文件格式")
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = f"uploads/{file_id}{file_extension}"
        
        # 创建上传目录
        os.makedirs("uploads", exist_ok=True)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"视频上传成功: {file_path}")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content)
        }
        
    except Exception as e:
        logger.error(f"视频上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.post("/analyze-video")
async def analyze_video(
    request: VideoAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """开始视频分析"""
    try:
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        analysis_tasks[task_id] = AnalysisProgress(
            task_id=task_id,
            status="pending",
            progress=0.0,
            current_frame=0,
            total_frames=0,
            message="准备开始分析..."
        )
        
        # 在后台执行分析任务
        background_tasks.add_task(
            run_video_analysis,
            task_id,
            request
        )
        
        logger.info(f"开始分析任务: {task_id}")
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "分析任务已开始"
        }
        
    except Exception as e:
        logger.error(f"启动分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动分析失败: {str(e)}")

@router.get("/analysis-progress/{task_id}")
async def get_analysis_progress(task_id: str):
    """获取分析进度"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return analysis_tasks[task_id]

@router.get("/analysis-result/{task_id}")
async def get_analysis_result(task_id: str):
    """获取分析结果"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = analysis_tasks[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="分析尚未完成")
    
    # 读取结果文件
    result_file = f"outputs/{task_id}_result.json"
    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="结果文件不存在")
    
    return FileResponse(result_file, media_type="application/json")

@router.get("/download-report/{task_id}")
async def download_report(task_id: str, format: str = "json"):
    """下载分析报告"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = analysis_tasks[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="分析尚未完成")
    
    # 根据格式返回不同的报告
    if format.lower() == "pdf":
        report_file = f"outputs/{task_id}_report.pdf"
        media_type = "application/pdf"
    elif format.lower() == "excel":
        report_file = f"outputs/{task_id}_report.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:  # json
        report_file = f"outputs/{task_id}_result.json"
        media_type = "application/json"
    
    if not os.path.exists(report_file):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(
        report_file,
        media_type=media_type,
        filename=f"video_analysis_report_{task_id}.{format}"
    )

@router.get("/video-formats")
async def get_video_formats(url: str):
    """获取视频的可用格式"""
    try:
        video_processor = VideoProcessor()
        
        formats_info = video_processor.list_available_formats(url)
        
        return {
            "success": True,
            "data": formats_info
        }
    except Exception as e:
        logger.error(f"获取视频格式失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"获取视频格式失败: {str(e)}")

async def run_video_analysis(task_id: str, request: VideoAnalysisRequest):
    """在后台运行视频分析"""
    try:
        # 更新任务状态
        analysis_tasks[task_id].status = "processing"
        analysis_tasks[task_id].message = "正在处理视频..."
        
        # 初始化服务
        video_processor = VideoProcessor()
        image_analyzer = ImageAnalyzer()
        report_generator = ReportGenerator()
        
        # 获取视频路径
        if request.video_url:
            # 下载在线视频（支持多个平台）
            analysis_tasks[task_id].message = "正在下载视频..."
            video_path = video_processor.download_online_video(request.video_url)
        else:
            video_path = request.video_file
        
        # 确保视频路径有效
        if not video_path:
            raise ValueError("无法获取有效的视频路径")
        
        # 获取视频信息
        video_info = video_processor.get_video_info(video_path)
        analysis_tasks[task_id].total_frames = video_info['total_frames']
        
        # 提取帧
        analysis_tasks[task_id].message = "正在提取视频帧..."
        frames = video_processor.extract_frames(video_path)
        
        # 分析每一帧
        frame_analyses = []
        for i, (frame_idx, timestamp, frame_path) in enumerate(frames):
            # 更新进度
            progress = (i + 1) / len(frames) * 100
            analysis_tasks[task_id].progress = progress
            analysis_tasks[task_id].current_frame = i + 1
            analysis_tasks[task_id].message = f"正在分析第 {i+1}/{len(frames)} 帧..."
            
            # 分析帧
            frame_analysis = image_analyzer.analyze_frame(frame_path)
            frame_analysis['frame_number'] = frame_idx
            frame_analysis['timestamp'] = timestamp
            frame_analyses.append(frame_analysis)
        
        # 音频分析
        analysis_tasks[task_id].message = "正在分析音频..."
        audio_analysis = video_processor.analyze_video_audio(video_path)
        
        # 计算综合评分
        overall_score = sum(frame['overall_score'] for frame in frame_analyses) / len(frame_analyses)
        
        # 生成分析结果
        result = {
            "video_id": task_id,
            "video_name": os.path.basename(video_path),
            "video_path": video_path,
            "duration": video_info['duration'],
            "total_frames": video_info['total_frames'],
            "analyzed_frames": len(frame_analyses),
            "analysis_time": 0,  # TODO: 计算实际分析时间
            "overall_quality_score": overall_score,
            "frame_analyses": frame_analyses,
            "audio_analysis": audio_analysis,
            "summary": {
                "avg_clarity": sum(f['clarity_score'] for f in frame_analyses) / len(frame_analyses),
                "avg_lighting": sum(f['lighting_score'] for f in frame_analyses) / len(frame_analyses),
                "face_detection_rate": sum(1 for f in frame_analyses if f['face_detected']) / len(frame_analyses),
                "watermark_detection_rate": sum(1 for f in frame_analyses if f['watermark_detected']) / len(frame_analyses),
                "avg_content_richness": sum(f['content_richness'] for f in frame_analyses) / len(frame_analyses),
                "audio_quality_score": audio_analysis.get('audio_quality', {}).get('quality_score', 0) if audio_analysis.get('success') else 0,
                "has_audio_transcription": audio_analysis.get('success', False) and bool(audio_analysis.get('transcription', {}).get('text', ''))
            }
        }
        
        # 保存结果
        os.makedirs("outputs", exist_ok=True)
        report_generator.save_json_result(result, f"outputs/{task_id}_result.json")
        report_generator.generate_pdf_report(result, f"outputs/{task_id}_report.pdf")
        report_generator.generate_excel_report(result, f"outputs/{task_id}_report.xlsx")
        
        # 清理临时文件
        frame_paths = [frame[2] for frame in frames]
        video_processor.cleanup_temp_files(frame_paths)
        
        # 更新任务状态
        analysis_tasks[task_id].status = "completed"
        analysis_tasks[task_id].progress = 100.0
        analysis_tasks[task_id].message = "分析完成"
        
        logger.info(f"分析任务完成: {task_id}")
        
    except Exception as e:
        logger.error(f"分析任务失败 {task_id}: {str(e)}")
        analysis_tasks[task_id].status = "failed"
        analysis_tasks[task_id].message = f"分析失败: {str(e)}" 