import cv2
import numpy as np
from PIL import Image
import easyocr
from transformers import CLIPProcessor, CLIPModel
from ultralytics import YOLO
import torch
from typing import Dict, List, Tuple, Optional
import logging
from config import Config
import os

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """图像分析服务"""
    
    def __init__(self):
        logger.info(f"使用设备: {Config.DEVICE}")
        # 初始化模型
        self._load_models()
    
    def _load_models(self):
        """加载所有分析模型"""
        try:
            # YOLOv8 模型
            self.yolo_model = YOLO('yolov8n.pt')
            self.yolo_model.to(Config.DEVICE)
            logger.info("YOLOv8 模型加载完成")
            
            # CLIP 模型
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(Config.DEVICE)
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            # 确保clip_processor是处理器实例而不是tuple
            if hasattr(self.clip_processor, '__getitem__') and isinstance(self.clip_processor, tuple):
                self.clip_processor = self.clip_processor[0]
            logger.info("CLIP 模型加载完成")
            
            # OCR 模型
            self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=(Config.DEVICE=="cuda"))
            logger.info("OCR 模型加载完成")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise
    
    def analyze_clarity(self, image_path: str) -> float:
        """分析图像清晰度（基于拉普拉斯算子）"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 计算拉普拉斯算子
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            # 转换为0-100的评分
            # 经验值：variance > 100 为清晰，< 50 为模糊
            if variance > 100:
                score = 100
            elif variance < 50:
                score = 0
            else:
                score = (variance - 50) * 2  # 线性映射
            
            return float(max(float(score), 0))
            
        except Exception as e:
            logger.error(f"清晰度分析失败: {str(e)}")
            return 0.0
    
    def analyze_lighting(self, image_path: str) -> float:
        """分析光照质量"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 计算直方图
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # 计算统计信息
            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)
            
            # 过曝检测（高亮度像素过多）
            overexposed_pixels = np.sum(gray > 240)
            overexposed_ratio = overexposed_pixels / (gray.shape[0] * gray.shape[1])
            
            # 欠曝检测（低亮度像素过多）
            underexposed_pixels = np.sum(gray < 20)
            underexposed_ratio = underexposed_pixels / (gray.shape[0] * gray.shape[1])
            
            # 评分计算
            score = 100
            
            # 过曝扣分
            if overexposed_ratio > 0.1:
                score -= (overexposed_ratio - 0.1) * 500
            
            # 欠曝扣分
            if underexposed_ratio > 0.1:
                score -= (underexposed_ratio - 0.1) * 500
            
            # 对比度扣分
            if std_brightness < 30:
                score -= (30 - std_brightness) * 2
            
            return float(max(float(score), 0))
            
        except Exception as e:
            logger.error(f"光照分析失败: {str(e)}")
            return 0.0
    
    def detect_faces(self, image_path: str) -> Tuple[bool, int]:
        """检测人脸"""
        try:
            results = self.yolo_model(image_path)
            
            face_count = 0
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls = int(box.cls[0])
                        # YOLOv8 中 person 类别为 0
                        if cls == 0:
                            face_count += 1
            
            return face_count > 0, face_count
            
        except Exception as e:
            logger.error(f"人脸检测失败: {str(e)}")
            return False, 0
    
    def detect_watermark(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """检测水印/文字"""
        try:
            # 检查图像文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"图像文件不存在: {image_path}")
                return False, None
            
            # 检查OCR模型是否正确加载
            if not hasattr(self, 'ocr_reader') or self.ocr_reader is None:
                logger.error("OCR模型未正确加载")
                return False, None
            
            # 验证图像文件是否可读
            try:
                test_image = cv2.imread(image_path)
                if test_image is None:
                    logger.error(f"无法读取图像文件: {image_path}")
                    return False, None
                logger.debug(f"图像尺寸: {test_image.shape}")
            except Exception as img_error:
                logger.error(f"图像读取失败: {str(img_error)}")
                return False, None
            
            # 使用OCR检测文字
            logger.debug(f"开始OCR检测: {image_path}")
            
            # 使用正确的easyocr API调用方式
            try:
                results = self.ocr_reader.readtext(image_path)
                logger.debug(f"OCR原始结果类型: {type(results)}")
                logger.debug(f"OCR原始结果: {results}")
            except Exception as ocr_error:
                logger.error(f"OCR调用失败: {str(ocr_error)}")
                return False, None

            if results and len(results) > 0:
                texts = []
                for result in results:
                    logger.debug(f"处理OCR结果项: {result}, 类型: {type(result)}")
                    
                    # easyocr返回格式: (bbox, text, confidence)
                    if isinstance(result, (list, tuple)) and len(result) >= 2:
                        text = str(result[1])  # 第二个元素是文字
                        confidence = result[2] if len(result) > 2 else 0
                        logger.debug(f"提取文字: '{text}', 置信度: {confidence}")
                        texts.append(text)
                    else:
                        logger.warning(f"意外的OCR结果格式: {result}")
                        texts.append(str(result))

                combined_text = ' '.join(texts)
                logger.debug(f"检测到的文字: {combined_text}")

                # 简单的水印判断逻辑
                watermark_keywords = ['watermark', 'logo', 'copyright', '©', '®', '™', '水印', '标志', '版权']
                is_watermark = any(keyword.lower() in combined_text.lower() for keyword in watermark_keywords)

                return True, combined_text if is_watermark else None
            else:
                logger.debug("OCR未检测到任何文字")
                return False, None

        except Exception as e:
            logger.error(f"水印检测失败: {str(e)}")
            logger.error(f"水印检测异常时OCR原始结果: {locals().get('results', None)}")
            # 返回默认值而不是抛出异常
            return False, None
    
    def analyze_content_richness(self, image_path: str) -> float:
        """分析内容丰富度（使用CLIP）"""
        try:
            # 预定义的丰富内容描述
            rich_descriptions = [
                "detailed scene with many objects",
                "complex composition with multiple elements",
                "rich visual content with various textures",
                "busy scene with lots of activity",
                "diverse visual elements and colors"
            ]
            
            poor_descriptions = [
                "simple background",
                "minimal content",
                "empty scene",
                "plain surface",
                "basic composition"
            ]
            
            # 加载图像
            image = Image.open(image_path)
            
            # 处理图像和文本
            inputs = self.clip_processor(
                text=rich_descriptions + poor_descriptions,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # 移动到设备
            for k, v in inputs.items():
                if hasattr(v, 'to'):
                    inputs[k] = v.to(Config.DEVICE)
            
            # 计算相似度
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                
                # 计算与丰富内容的平均相似度
                rich_scores = logits_per_image[0, :len(rich_descriptions)]
                poor_scores = logits_per_image[0, len(rich_descriptions):]
                
                avg_rich_score = torch.mean(rich_scores).item()
                avg_poor_score = torch.mean(poor_scores).item()
                
                # 转换为0-100评分
                score = (avg_rich_score - avg_poor_score + 2) * 25  # 假设分数范围在-2到2之间
                score = max(0, min(100, score))
                
                return score
                
        except Exception as e:
            logger.error(f"内容丰富度分析失败: {str(e)}")
            return 50.0  # 返回中等分数
    
    def analyze_frame(self, image_path: str) -> Dict:
        """综合分析单帧图像"""
        try:
            logger.info(f"开始分析帧: {image_path}")
            
            # 并行分析各项指标
            clarity_score = self.analyze_clarity(image_path)
            lighting_score = self.analyze_lighting(image_path)
            face_detected, face_count = self.detect_faces(image_path)
            watermark_detected, watermark_text = self.detect_watermark(image_path)
            content_richness = self.analyze_content_richness(image_path)
            
            # 计算综合评分
            weights = {
                'clarity': 0.3,
                'lighting': 0.25,
                'content': 0.25,
                'face': 0.1,
                'watermark': 0.1
            }
            
            overall_score = (
                clarity_score * weights['clarity'] +
                lighting_score * weights['lighting'] +
                content_richness * weights['content'] +
                (100 if not watermark_detected else 50) * weights['watermark'] +
                (100 if face_detected else 70) * weights['face']
            )
            
            # 收集问题
            issues = []
            if clarity_score < 50:
                issues.append("图像模糊")
            if lighting_score < 50:
                issues.append("光照问题")
            if watermark_detected:
                issues.append("检测到水印")
            if content_richness < 30:
                issues.append("内容单调")
            
            result = {
                'clarity_score': clarity_score,
                'lighting_score': lighting_score,
                'face_detected': face_detected,
                'face_count': face_count,
                'watermark_detected': watermark_detected,
                'watermark_text': watermark_text,
                'content_richness': content_richness,
                'overall_score': overall_score,
                'issues': issues
            }
            
            logger.info(f"帧分析完成: 综合评分 {overall_score:.1f}")
            return result
            
        except Exception as e:
            logger.error(f"帧分析失败: {str(e)}")
            return {
                'clarity_score': 0,
                'lighting_score': 0,
                'face_detected': False,
                'face_count': 0,
                'watermark_detected': False,
                'watermark_text': None,
                'content_richness': 0,
                'overall_score': 0,
                'issues': [f"分析失败: {str(e)}"]
            } 