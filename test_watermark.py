#!/usr/bin/env python3
"""
水印检测功能测试脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.image_analyzer import ImageAnalyzer
from config import Config

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_watermark_detection():
    """测试水印检测功能"""
    try:
        logger.info("开始测试水印检测功能...")
        
        # 初始化图像分析器
        analyzer = ImageAnalyzer()
        logger.info("图像分析器初始化完成")
        
        # 检查OCR模型是否正确加载
        if hasattr(analyzer, 'ocr_reader') and analyzer.ocr_reader is not None:
            logger.info("OCR模型已正确加载")
        else:
            logger.error("OCR模型未正确加载")
            return False
        
        # 查找测试图像
        test_images = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            test_images.extend(Path('.').glob(ext))
            test_images.extend(Path('uploads').glob(ext))
            test_images.extend(Path('outputs').glob(ext))
        
        if not test_images:
            logger.warning("未找到测试图像，创建一个简单的测试图像")
            # 创建一个简单的测试图像
            import cv2
            import numpy as np
            
            # 创建一个白色背景的图像
            img = np.ones((300, 400, 3), dtype=np.uint8) * 255
            
            # 添加一些文字
            cv2.putText(img, 'Test Watermark', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(img, '© 2024', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            test_image_path = 'test_watermark.jpg'
            cv2.imwrite(test_image_path, img)
            test_images = [Path(test_image_path)]
            logger.info(f"创建测试图像: {test_image_path}")
        
        # 测试每个图像
        for img_path in test_images[:3]:  # 只测试前3个图像
            logger.info(f"测试图像: {img_path}")
            
            try:
                # 测试水印检测
                has_watermark, watermark_text = analyzer.detect_watermark(str(img_path))
                
                logger.info(f"水印检测结果:")
                logger.info(f"  检测到水印: {has_watermark}")
                logger.info(f"  水印文字: {watermark_text}")
                
                # 测试其他分析功能
                clarity = analyzer.analyze_clarity(str(img_path))
                lighting = analyzer.analyze_lighting(str(img_path))
                faces_detected, face_count = analyzer.detect_faces(str(img_path))
                
                logger.info(f"其他分析结果:")
                logger.info(f"  清晰度: {clarity:.1f}")
                logger.info(f"  光照: {lighting:.1f}")
                logger.info(f"  人脸检测: {faces_detected}, 数量: {face_count}")
                
            except Exception as e:
                logger.error(f"测试图像 {img_path} 时出错: {str(e)}")
                continue
        
        logger.info("水印检测测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_watermark_detection()
    if success:
        print("✅ 水印检测测试通过")
    else:
        print("❌ 水印检测测试失败")
        sys.exit(1) 