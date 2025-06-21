import cv2
import os
import yt_dlp
import tempfile
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    """视频处理服务"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        # 延迟初始化音频处理器，避免依赖问题
        self._audio_processor = None
    
    def _get_audio_processor(self):
        """延迟初始化音频处理器"""
        if self._audio_processor is None:
            try:
                # 尝试多种导入方式
                try:
                    from app.services.audio_processor import AudioProcessor
                except ImportError:
                    try:
                        import sys
                        sys.path.append(os.path.dirname(__file__))
                        from audio_processor import AudioProcessor
                    except ImportError:
                        # 如果还是失败，尝试相对导入
                        from .audio_processor import AudioProcessor
                
                self._audio_processor = AudioProcessor()
                logger.info("音频处理器初始化成功")
            except ImportError as e:
                logger.warning(f"音频处理器导入失败: {str(e)}")
                return None
            except Exception as e:
                logger.warning(f"音频处理器初始化失败: {str(e)}")
                return None
        return self._audio_processor
    
    def process_video_with_audio(self, video_path: str) -> Dict:
        """处理视频（包括音频分析）"""
        try:
            logger.info(f"开始处理视频（含音频）: {video_path}")
            
            # 获取视频信息
            video_info = self.get_video_info(video_path)
            
            # 提取帧
            frames = self.extract_frames(video_path)
            
            # 音频分析
            audio_result = self.analyze_video_audio(video_path)
            
            result = {
                'video_info': video_info,
                'frames': frames,
                'audio_analysis': audio_result,
                'total_frames_analyzed': len(frames)
            }
            
            logger.info("视频处理完成（含音频分析）")
            return result
            
        except Exception as e:
            logger.error(f"视频处理失败: {str(e)}")
            raise
    
    def analyze_video_audio(self, video_path: str) -> Dict:
        """分析视频中的音频"""
        try:
            audio_processor = self._get_audio_processor()
            if audio_processor is None:
                return {
                    'success': False,
                    'error': '音频处理器未初始化',
                    'transcription': {},
                    'audio_quality': {}
                }
            
            return audio_processor.process_video_audio(video_path)
            
        except Exception as e:
            logger.error(f"音频分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transcription': {},
                'audio_quality': {}
            }
    
    def download_online_video(self, url: str, output_dir: str = "downloads") -> str:
        """下载在线视频（支持多个平台）"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 检测URL类型
            url_type = self._detect_url_type(url)
            logger.info(f"检测到URL类型: {url_type}")
            
            # 尝试不同的下载策略
            download_strategies = [
                self._try_download_with_format_preference,
                self._try_download_with_basic_format,
                self._try_download_with_minimal_requirements
            ]
            
            for i, strategy in enumerate(download_strategies):
                try:
                    logger.info(f"尝试下载策略 {i+1}/{len(download_strategies)}")
                    video_path = strategy(url, url_type, output_dir)
                    if video_path and os.path.exists(video_path):
                        logger.info(f"视频下载成功: {video_path}")
                        return video_path
                except Exception as e:
                    logger.warning(f"下载策略 {i+1} 失败: {str(e)}")
                    continue
            
            # 所有策略都失败了
            raise Exception("所有下载策略都失败了，请检查URL是否有效或视频是否可访问")
            
        except Exception as e:
            logger.error(f"下载视频失败: {str(e)}")
            raise
    
    def _try_download_with_format_preference(self, url: str, url_type: str, output_dir: str) -> str:
        """尝试使用首选格式下载"""
        ydl_opts = self._get_download_options(url_type, output_dir)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 先获取视频信息
            logger.info(f"正在获取视频信息: {url}")
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                raise ValueError("无法获取视频信息，请检查URL是否有效")
            
            # 检查视频时长，避免下载过长的视频
            duration = info.get('duration', 0)
            if duration > 3600:  # 超过1小时
                logger.warning(f"视频时长过长 ({duration}秒)，可能影响分析速度")
            
            # 检查文件大小
            filesize = info.get('filesize', 0)
            if filesize > 500 * 1024 * 1024:  # 超过500MB
                logger.warning(f"视频文件过大 ({filesize / 1024 / 1024:.1f}MB)，可能影响下载速度")
            
            # 开始下载
            logger.info(f"开始下载视频: {info.get('title', 'Unknown')}")
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            return video_path
    
    def _try_download_with_basic_format(self, url: str, url_type: str, output_dir: str) -> str:
        """尝试使用基本格式下载"""
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            'format': 'best',  # 只选择最佳格式，不限制大小
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("尝试使用基本格式下载")
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            return video_path
    
    def _try_download_with_minimal_requirements(self, url: str, url_type: str, output_dir: str) -> str:
        """尝试使用最小要求下载"""
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,  # 忽略错误
            'nocheckcertificate': True,
            'format': 'worst',  # 选择最差格式，确保能下载
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("尝试使用最小要求下载")
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            return video_path
    
    def _detect_url_type(self, url: str) -> str:
        """检测URL类型"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'bilibili.com' in url_lower:
            return 'bilibili'
        elif 'douyin.com' in url_lower or 'tiktok.com' in url_lower:
            return 'short_video'
        elif 'weibo.com' in url_lower:
            return 'weibo'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'facebook.com' in url_lower:
            return 'facebook'
        elif 'vk.com' in url_lower:
            return 'vk'
        else:
            return 'generic'
    
    def _get_download_options(self, url_type: str, output_dir: str) -> dict:
        """根据URL类型获取下载选项"""
        base_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            'extract_flat': False,
        }
        
        # 根据平台调整下载选项
        if url_type == 'youtube':
            base_opts.update({
                'format': 'best[filesize<500M][height<=1080]/best[filesize<500M]/best',
                'writeinfojson': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['zh-CN', 'en'],
            })
        elif url_type == 'bilibili':
            base_opts.update({
                'format': 'best[filesize<500M]/best',
                'cookies': 'cookies.txt',  # 如果需要登录
            })
        elif url_type == 'short_video':
            base_opts.update({
                'format': 'best',
                'extract_flat': False,
            })
        elif url_type == 'weibo':
            base_opts.update({
                'format': 'best[filesize<200M]/best',
                'cookies': 'cookies.txt',
            })
        else:
            # 通用配置 - 更灵活的格式选择
            base_opts.update({
                'format': 'best[filesize<500M]/best[ext=mp4]/best[ext=webm]/best',
                'extract_flat': False,
            })
        
        return base_opts
    
    def download_youtube_video(self, url: str, output_dir: str = "downloads") -> str:
        """下载YouTube视频（保持向后兼容）"""
        logger.warning("download_youtube_video 方法已弃用，请使用 download_online_video")
        return self.download_online_video(url, output_dir)
    
    def extract_frames(self, video_path: str, interval: int = 5) -> List[Tuple[int, float, str]]:
        """每interval秒提取一帧"""
        frames = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("无法打开视频文件")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            # 计算需要提取的帧
            frame_interval = int(fps * interval)
            frame_positions = list(range(0, total_frames, frame_interval))
            
            logger.info(f"视频信息: {total_frames}帧, {fps}fps, {duration:.2f}秒")
            logger.info(f"将提取 {len(frame_positions)} 帧")
            
            for i, frame_pos in enumerate(frame_positions):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if ret:
                    timestamp = frame_pos / fps
                    
                    # 保存帧到临时文件
                    frame_filename = f"frame_{i:04d}_{timestamp:.2f}s.jpg"
                    frame_path = os.path.join("temp_frames", frame_filename)
                    os.makedirs("temp_frames", exist_ok=True)
                    
                    cv2.imwrite(frame_path, frame)
                    frames.append((i, timestamp, frame_path))
                    
                    logger.debug(f"提取帧 {i}: {timestamp:.2f}s -> {frame_path}")
            
            cap.release()
            logger.info(f"成功提取 {len(frames)} 帧")
            return frames
            
        except Exception as e:
            logger.error(f"提取帧失败: {str(e)}")
            raise
    
    def get_video_info(self, video_path: str) -> dict:
        """获取视频基本信息"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("无法打开视频文件")
            
            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS),
                'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
                'file_size': os.path.getsize(video_path) if os.path.exists(video_path) else 0
            }
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            raise
    
    def cleanup_temp_files(self, frame_paths: List[str]):
        """清理临时文件"""
        for frame_path in frame_paths:
            try:
                if os.path.exists(frame_path):
                    os.remove(frame_path)
            except Exception as e:
                logger.warning(f"清理临时文件失败 {frame_path}: {str(e)}")
        
        # 清理临时目录
        try:
            if os.path.exists("temp_frames") and not os.listdir("temp_frames"):
                os.rmdir("temp_frames")
        except Exception as e:
            logger.warning(f"清理临时目录失败: {str(e)}")
    
    def list_available_formats(self, url: str) -> dict:
        """列出视频的可用格式"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"正在获取视频格式信息: {url}")
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    raise ValueError("无法获取视频信息")
                
                formats = info.get('formats', [])
                available_formats = []
                
                for fmt in formats:
                    format_info = {
                        'format_id': fmt.get('format_id', 'N/A'),
                        'ext': fmt.get('ext', 'N/A'),
                        'resolution': fmt.get('resolution', 'N/A'),
                        'filesize': fmt.get('filesize', 0),
                        'vcodec': fmt.get('vcodec', 'N/A'),
                        'acodec': fmt.get('acodec', 'N/A'),
                        'fps': fmt.get('fps', 'N/A'),
                    }
                    available_formats.append(format_info)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'formats': available_formats
                }
                
        except Exception as e:
            logger.error(f"获取格式信息失败: {str(e)}")
            raise 