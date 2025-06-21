# 🎬 Video Quality Analyzer（视频质量分析器）

> 作者微信：lala604635

## 📖 项目简介

一个智能视频质量分析工具，支持本地视频文件和多种在线视频平台的自动质量评估。通过AI技术对视频进行多维度分析，生成专业的质量报告。

## ✨ 核心功能

### 🎯 多源视频支持
- **本地文件**：支持 MP4、AVI、MOV、MKV、WMV、FLV 等主流格式
- **在线视频**：支持 YouTube、Bilibili、抖音/TikTok、微博、Twitter/X、Instagram、Facebook、VK 等平台
- **智能下载**：自动检测平台类型，优化下载策略

### 🔍 智能分析引擎
- **清晰度分析**：基于拉普拉斯算子的图像清晰度评估
- **光照质量**：过曝/欠曝检测，对比度分析
- **人脸检测**：基于YOLOv8的人脸识别和计数
- **水印识别**：OCR文字检测，智能水印判断
- **内容丰富度**：基于CLIP模型的内容复杂度评估
- **音频转录**：Whisper语音识别，分段时间戳

### 📊 综合评分系统
- **0-100分制**：多维度加权计算
- **实时进度**：Web界面实时显示分析进度
- **问题诊断**：自动识别和报告质量问题

### 📄 多格式报告
- **JSON格式**：结构化数据，便于程序处理
- **PDF报告**：专业排版，包含图表和详细分析
- **Excel表格**：数据透视，便于进一步分析

## 🌐 支持的在线视频平台

| 平台 | 支持状态 | 特殊配置 | 备注 |
|------|----------|----------|------|
| YouTube | ✅ 完整支持 | 字幕下载、格式优化 | 全球最大视频平台 |
| Bilibili | ✅ 完整支持 | 需要登录cookie | 中国领先视频网站 |
| 抖音/TikTok | ✅ 完整支持 | 短视频优化 | 短视频平台 |
| 微博 | ✅ 完整支持 | 文件大小限制 | 社交媒体视频 |
| Twitter/X | ✅ 完整支持 | 格式自动选择 | 社交媒体视频 |
| Instagram | ✅ 完整支持 | 图片视频混合 | 图片视频分享 |
| Facebook | ✅ 完整支持 | 隐私设置处理 | 社交媒体视频 |
| VK | ✅ 完整支持 | 俄语内容支持 | 俄罗斯社交网络 |
| 其他平台 | ✅ 通用支持 | 通过yt-dlp支持 | 兼容性保证 |

## 🚀 快速开始

### 环境要求

- **操作系统**：Windows 10/11、Linux、macOS
- **Python版本**：3.8+
- **内存要求**：8GB+ RAM
- **存储空间**：2GB+ 可用空间
- **推荐配置**：NVIDIA GPU (CUDA 12.1) 用于加速

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd video-quality-analyzer
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **启动服务**
```bash
# 开发模式（推荐）
uvicorn main:app --reload --log-level debug

# 生产模式
python main.py
```

5. **访问界面**
打开浏览器访问：http://localhost:8000

## 📁 项目结构

```
video-quality-analyzer/
├── main.py                 # 应用入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── README.md             # 项目文档
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py     # API路由
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py    # 数据模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_processor.py    # 视频处理
│   │   ├── image_analyzer.py     # 图像分析
│   │   └── audio_processor.py    # 音频处理
│   └── utils/
│       ├── __init__.py
│       └── report_generator.py   # 报告生成
├── static/
│   └── fonts/
│       └── msyh.ttc      # 中文字体
├── templates/
│   └── index.html        # 前端页面
├── uploads/              # 上传文件目录
├── downloads/            # 下载文件目录
├── outputs/              # 输出文件目录
└── reports/              # 报告文件目录
```

## 🔧 配置说明

### 主要配置项（config.py）

```python
class Config:
    # 设备配置
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    
    # 文件配置
    UPLOAD_DIR = "uploads"
    DOWNLOAD_DIR = "downloads"
    OUTPUT_DIR = "outputs"
    REPORT_DIR = "reports"
    
    # 分析配置
    FRAME_INTERVAL = 5  # 帧提取间隔（秒）
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 最大视频大小（500MB）
```

## 📡 API 文档

### 核心接口

#### 1. 上传视频文件
```http
POST /api/upload-video
Content-Type: multipart/form-data

file: [视频文件]
```

#### 2. 分析视频
```http
POST /api/analyze-video
Content-Type: application/json

{
    "video_file": "uploads/xxx.mp4",
    "video_url": "https://youtube.com/watch?v=xxx"
}
```

#### 3. 查询分析进度
```http
GET /api/analysis-progress/{task_id}
```

#### 4. 获取分析结果
```http
GET /api/analysis-result/{task_id}
```

#### 5. 下载报告
```http
GET /api/download-report/{task_id}?format={json|pdf|excel}
```

#### 6. 查询视频格式
```http
GET /api/video-formats?url={video_url}
```

### 响应格式

#### 分析结果示例
```json
{
    "task_id": "uuid",
    "overall_quality_score": 85.5,
    "summary": {
        "avg_clarity": 78.2,
        "avg_lighting": 82.1,
        "avg_content_richness": 75.8,
        "face_detection_rate": 0.6,
        "watermark_detection_rate": 0.1
    },
    "frame_analyses": [...],
    "audio_analysis": {
        "transcription": {
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.0,
                    "text": "这是第一段音频内容"
                }
            ]
        }
    }
}
```

## 🎨 前端界面

### 主要功能
- **拖拽上传**：支持拖拽文件到指定区域
- **在线链接**：支持粘贴视频链接
- **格式检查**：预览视频可用格式
- **实时进度**：进度条和状态消息
- **结果展示**：图表化展示分析结果
- **报告下载**：一键下载多种格式报告

### 界面截图
- 上传界面：支持文件和链接两种方式
- 分析进度：实时显示处理状态
- 结果展示：综合评分和详细分析
- 音频转录：分段显示语音内容

## 🔍 技术架构

### 核心技术栈
- **后端框架**：FastAPI + Uvicorn
- **AI模型**：YOLOv8 + CLIP + EasyOCR + Whisper
- **图像处理**：OpenCV + PIL
- **视频处理**：MoviePy + yt-dlp
- **报告生成**：ReportLab + openpyxl
- **前端技术**：HTML5 + Bootstrap + JavaScript

### 模型说明
- **YOLOv8**：目标检测，用于人脸识别
- **CLIP**：图像-文本对比学习，用于内容丰富度分析
- **EasyOCR**：光学字符识别，用于水印检测
- **Whisper**：语音识别，用于音频转录

## 🚀 性能优化

### GPU加速
- 自动检测CUDA环境
- 模型自动迁移到GPU
- 支持多GPU并行处理

### 内存优化
- 流式处理大文件
- 及时释放内存
- 分帧处理避免内存溢出

### 下载优化
- 多策略下载机制
- 格式自动降级
- 断点续传支持

## 🐛 故障排除

### 常见问题

#### 1. 模型加载失败
```bash
# 检查CUDA环境
python -c "import torch; print(torch.cuda.is_available())"

# 重新安装PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### 2. 视频下载失败
- 检查网络连接
- 验证视频链接有效性
- 尝试"检查格式"功能
- 查看详细错误日志

#### 3. 水印检测异常
- 确保OCR模型正确加载
- 检查图像文件完整性
- 查看调试日志定位问题

#### 4. 内存不足
- 减少并发处理数量
- 降低视频分辨率
- 增加系统内存

### 日志查看
```bash
# 启动时查看详细日志
uvicorn main:app --reload --log-level debug

# 查看应用日志
tail -f app.log
```

## 📈 开发计划

### 近期计划
- [ ] 支持更多视频格式
- [ ] 增加批量处理功能
- [ ] 优化GPU内存使用
- [ ] 添加更多分析指标

### 长期计划
- [ ] 支持实时视频流分析
- [ ] 集成更多AI模型
- [ ] 开发移动端应用
- [ ] 支持云端部署

## 🤝 贡献指南

### 开发环境设置
1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 规范
- 添加适当的注释
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- **作者微信**：lala604635

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenAI CLIP](https://github.com/openai/CLIP)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

---

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！** 