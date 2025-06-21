from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class VideoAnalysisRequest(BaseModel):
    """视频分析请求模型"""
    video_url: Optional[str] = None
    video_file: Optional[str] = None
    analysis_type: str = "full"  # full, quick, custom

class FrameAnalysis(BaseModel):
    """单帧分析结果"""
    frame_number: int
    timestamp: float
    clarity_score: float  # 清晰度评分 0-100
    lighting_score: float  # 光照评分 0-100
    face_detected: bool
    face_count: int
    watermark_detected: bool
    watermark_text: Optional[str] = None
    content_richness: float  # 内容丰富度 0-100
    overall_score: float  # 综合评分 0-100
    issues: List[str] = []  # 发现的问题

class VideoAnalysisResult(BaseModel):
    """视频分析结果"""
    video_id: str
    video_name: str
    video_path: str
    duration: float
    total_frames: int
    analyzed_frames: int
    analysis_time: float
    overall_quality_score: float
    frame_analyses: List[FrameAnalysis]
    summary: Dict[str, Any]
    created_at: datetime

class AnalysisProgress(BaseModel):
    """分析进度"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0-100
    current_frame: int
    total_frames: int
    message: str
    estimated_time: Optional[float] = None

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None 