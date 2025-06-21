import os
from typing import Dict, Any
import torch

class Config:
    """应用配置"""
    
    # 基础配置
    APP_NAME = "视频质量分析器"
    APP_VERSION = "1.0.0"
    DEBUG = True
    
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    
    # 文件路径配置
    UPLOAD_DIR = "uploads"
    OUTPUT_DIR = "outputs"
    TEMP_DIR = "temp_frames"
    DOWNLOAD_DIR = "downloads"
    
    # 视频处理配置
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    FRAME_EXTRACTION_INTERVAL = 5  # 每5秒提取一帧
    
    # 模型配置
    YOLO_MODEL = "yolov8n.pt"
    CLIP_MODEL = "openai/clip-vit-base-patch32"
    OCR_LANGUAGES = ['ch_sim', 'en']
    
    # 分析配置
    ANALYSIS_WEIGHTS = {
        'clarity': 0.3,
        'lighting': 0.25,
        'content': 0.25,
        'face': 0.1,
        'watermark': 0.1
    }
    
    # 评分阈值
    CLARITY_THRESHOLD = 50
    LIGHTING_THRESHOLD = 50
    CONTENT_THRESHOLD = 30
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "app.log"
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    @classmethod
    def get_upload_path(cls) -> str:
        """获取上传目录路径"""
        return os.path.abspath(cls.UPLOAD_DIR)
    
    @classmethod
    def get_output_path(cls) -> str:
        """获取输出目录路径"""
        return os.path.abspath(cls.OUTPUT_DIR)
    
    @classmethod
    def get_temp_path(cls) -> str:
        """获取临时目录路径"""
        return os.path.abspath(cls.TEMP_DIR)
    
    @classmethod
    def get_download_path(cls) -> str:
        """获取下载目录路径"""
        return os.path.abspath(cls.DOWNLOAD_DIR)
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录"""
        directories = [
            cls.UPLOAD_DIR,
            cls.OUTPUT_DIR,
            cls.TEMP_DIR,
            cls.DOWNLOAD_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """获取模型配置"""
        return {
            'yolo_model': cls.YOLO_MODEL,
            'clip_model': cls.CLIP_MODEL,
            'ocr_languages': cls.OCR_LANGUAGES
        }
    
    @classmethod
    def get_analysis_config(cls) -> Dict[str, Any]:
        """获取分析配置"""
        return {
            'weights': cls.ANALYSIS_WEIGHTS,
            'thresholds': {
                'clarity': cls.CLARITY_THRESHOLD,
                'lighting': cls.LIGHTING_THRESHOLD,
                'content': cls.CONTENT_THRESHOLD
            },
            'frame_interval': cls.FRAME_EXTRACTION_INTERVAL
        } 