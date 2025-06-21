import os
import logging
import tempfile
from typing import Dict, List, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

class AudioProcessor:
    """音频处理服务"""
    
    def __init__(self):
        self.device = Config.DEVICE
        logger.info(f"音频处理器使用设备: {self.device}")
        
        # 延迟初始化模型，避免启动时的问题
        self._whisper_model = None
        self._recognizer = None
    
    def _load_whisper_model(self):
        """延迟加载Whisper模型"""
        if self._whisper_model is None:
            try:
                import whisper
                self._whisper_model = whisper.load_model("base").to(self.device)
                logger.info("Whisper模型加载完成")
            except Exception as e:
                logger.warning(f"Whisper模型加载失败: {str(e)}")
                return None
        return self._whisper_model
    
    def _load_speech_recognizer(self):
        """延迟加载语音识别器"""
        if self._recognizer is None:
            try:
                import speech_recognition as sr
                self._recognizer = sr.Recognizer()
                logger.info("语音识别器初始化完成")
            except Exception as e:
                logger.warning(f"语音识别器初始化失败: {str(e)}")
                return None
        return self._recognizer
    
    def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """从视频中提取音频"""
        try:
            logger.info(f"开始从视频提取音频: {video_path}")
            
            # 创建临时音频文件
            temp_audio_path = tempfile.mktemp(suffix='.wav')
            
            # 使用moviepy提取音频
            try:
                import moviepy.editor as mp
                video = mp.VideoFileClip(video_path)
                audio = video.audio
                
                if audio is None:
                    logger.warning("视频中没有音频轨道")
                    return None
                
                # 保存音频文件
                audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                video.close()
                
                logger.info(f"音频提取完成: {temp_audio_path}")
                return temp_audio_path
                
            except ImportError as e:
                logger.warning(f"moviepy导入失败: {str(e)}")
                return None
            except Exception as e:
                logger.warning(f"moviepy音频提取失败: {str(e)}")
                return None
            
        except Exception as e:
            logger.error(f"音频提取失败: {str(e)}")
            return None
    
    def transcribe_audio_whisper(self, audio_path: str) -> Dict:
        """使用Whisper进行语音识别"""
        try:
            logger.info(f"开始Whisper语音识别: {audio_path}")
            
            whisper_model = self._load_whisper_model()
            if whisper_model is None:
                return {
                    'text': '',
                    'segments': [],
                    'language': 'unknown',
                    'duration': 0,
                    'error': 'Whisper模型未加载'
                }
            
            # 使用Whisper进行转录
            result = whisper_model.transcribe(
                audio_path,
                language="zh",  # 支持中文
                task="transcribe"
            )
            
            transcription = {
                'text': result['text'],
                'segments': result.get('segments', []),
                'language': result.get('language', 'unknown'),
                'duration': result.get('duration', 0)
            }
            
            logger.info(f"Whisper识别完成，文本长度: {len(transcription['text'])}")
            return transcription
            
        except Exception as e:
            logger.error(f"Whisper识别失败: {str(e)}")
            return {
                'text': '',
                'segments': [],
                'language': 'unknown',
                'duration': 0,
                'error': str(e)
            }
    
    def analyze_audio_quality(self, audio_path: str) -> Dict:
        """分析音频质量"""
        try:
            logger.info(f"开始分析音频质量: {audio_path}")
            
            # 使用pydub分析音频
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(audio_path)
                
                # 计算音频统计信息
                duration = len(audio) / 1000.0  # 转换为秒
                sample_rate = audio.frame_rate
                channels = audio.channels
                
                # 计算音量统计
                samples = audio.get_array_of_samples()
                if channels == 2:
                    # 立体声，取平均值
                    samples = [sum(samples[i:i+2])/2 for i in range(0, len(samples), 2)]
                
                # 计算音量统计
                volume_stats = {
                    'min': min(samples),
                    'max': max(samples),
                    'mean': sum(samples) / len(samples),
                    'rms': (sum(x*x for x in samples) / len(samples)) ** 0.5
                }
                
                # 计算动态范围
                dynamic_range = 20 * (volume_stats['max'] - volume_stats['min']) / 32768
                
                # 音频质量评分
                quality_score = 100
                
                # 音量过低扣分
                if volume_stats['rms'] < 1000:
                    quality_score -= 20
                
                # 动态范围过小扣分
                if dynamic_range < 20:
                    quality_score -= 15
                
                # 采样率过低扣分
                if sample_rate < 22050:
                    quality_score -= 10
                
                # 时长过短扣分
                if duration < 1:
                    quality_score -= 30
                
                quality_score = max(0, quality_score)
                
                result = {
                    'duration': duration,
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'volume_stats': volume_stats,
                    'dynamic_range': dynamic_range,
                    'quality_score': quality_score,
                    'issues': []
                }
                
                # 收集问题
                if volume_stats['rms'] < 1000:
                    result['issues'].append("音量过低")
                if dynamic_range < 20:
                    result['issues'].append("动态范围小")
                if sample_rate < 22050:
                    result['issues'].append("采样率较低")
                if duration < 1:
                    result['issues'].append("音频时长过短")
                
                logger.info(f"音频质量分析完成，评分: {quality_score}")
                return result
                
            except ImportError:
                logger.warning("pydub未安装，无法进行详细音频分析")
                return {
                    'duration': 0,
                    'sample_rate': 0,
                    'channels': 0,
                    'volume_stats': {},
                    'dynamic_range': 0,
                    'quality_score': 50,  # 默认中等分数
                    'issues': ["无法进行详细音频分析"]
                }
            
        except Exception as e:
            logger.error(f"音频质量分析失败: {str(e)}")
            return {
                'duration': 0,
                'sample_rate': 0,
                'channels': 0,
                'volume_stats': {},
                'dynamic_range': 0,
                'quality_score': 0,
                'issues': [f"分析失败: {str(e)}"]
            }
    
    def process_video_audio(self, video_path: str) -> Dict:
        """处理视频音频的完整流程"""
        try:
            logger.info(f"开始处理视频音频: {video_path}")
            
            # 1. 提取音频
            audio_path = self.extract_audio_from_video(video_path)
            if not audio_path:
                return {
                    'success': False,
                    'error': '无法从视频中提取音频',
                    'transcription': {},
                    'audio_quality': {}
                }
            
            # 2. 语音识别
            transcription = self.transcribe_audio_whisper(audio_path)
            
            # 3. 音频质量分析
            audio_quality = self.analyze_audio_quality(audio_path)
            
            # 4. 清理临时文件
            try:
                os.remove(audio_path)
                logger.info("临时音频文件已清理")
            except:
                pass
            
            result = {
                'success': True,
                'transcription': transcription,
                'audio_quality': audio_quality
            }
            
            logger.info("视频音频处理完成")
            return result
            
        except Exception as e:
            logger.error(f"视频音频处理失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transcription': {},
                'audio_quality': {}
            } 