import json
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, Any, List
import logging
import os

logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_chinese_font()
    
    def _register_chinese_font(self):
        """注册中文字体"""
        try:
            font_path = os.path.join('static', 'fonts', 'msyh.ttc')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('MSYH', font_path))
                logger.info("中文字体注册成功")
            else:
                logger.warning("中文字体文件不存在，使用默认字体")
        except Exception as e:
            logger.warning(f"中文字体注册失败: {str(e)}")
    
    def _get_chinese_style(self, style_name, **kwargs):
        """获取支持中文的样式"""
        try:
            base_style = self.styles[style_name]
            chinese_style = ParagraphStyle(
                f'Chinese{style_name}',
                parent=base_style,
                fontName='MSYH',
                **kwargs
            )
            return chinese_style
        except:
            return self.styles[style_name]
    
    def save_json_result(self, result: Dict[str, Any], file_path: str):
        """保存JSON格式结果"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON结果已保存: {file_path}")
        except Exception as e:
            logger.error(f"保存JSON结果失败: {str(e)}")
            raise
    
    def generate_pdf_report(self, result: Dict[str, Any], file_path: str):
        """生成PDF报告"""
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # 标题
            title_style = self._get_chinese_style(
                'Heading1',
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("视频质量分析报告", title_style))
            story.append(Spacer(1, 20))
            
            # 基本信息
            story.append(Paragraph("基本信息", self._get_chinese_style('Heading2')))
            story.append(Spacer(1, 12))
            
            basic_info_data = [
                ["视频名称", result.get('video_name', 'N/A')],
                ["视频时长", f"{result.get('duration', 0):.2f} 秒"],
                ["总帧数", str(result.get('total_frames', 0))],
                ["分析帧数", str(result.get('analyzed_frames', 0))],
                ["综合质量评分", f"{result.get('overall_quality_score', 0):.1f}/100"]
            ]
            basic_info = [[Paragraph(str(cell), self._get_chinese_style('Normal')) for cell in row] for row in basic_info_data]
            
            basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
            basic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'MSYH'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(basic_table)
            story.append(Spacer(1, 20))
            
            # 分析摘要
            story.append(Paragraph("分析摘要", self._get_chinese_style('Heading2')))
            story.append(Spacer(1, 12))
            
            summary = result.get('summary', {})
            summary_info_data = [
                ["平均清晰度", f"{summary.get('avg_clarity', 0):.1f}/100"],
                ["平均光照质量", f"{summary.get('avg_lighting', 0):.1f}/100"],
                ["人脸检测率", f"{summary.get('face_detection_rate', 0)*100:.1f}%"],
                ["水印检测率", f"{summary.get('watermark_detection_rate', 0)*100:.1f}%"],
                ["平均内容丰富度", f"{summary.get('avg_content_richness', 0):.1f}/100"],
                ["音频质量评分", f"{summary.get('audio_quality_score', 0):.1f}/100"],
                ["音频转录状态", "有转录" if summary.get('has_audio_transcription', False) else "无转录"]
            ]
            summary_info = [[Paragraph(str(cell), self._get_chinese_style('Normal')) for cell in row] for row in summary_info_data]
            
            summary_table = Table(summary_info, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'MSYH'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # 音频分析结果
            audio_analysis = result.get('audio_analysis', {})
            if audio_analysis.get('success', False):
                story.append(Paragraph("音频分析结果", self._get_chinese_style('Heading2')))
                story.append(Spacer(1, 12))
                
                transcription = audio_analysis.get('transcription', {})
                audio_quality = audio_analysis.get('audio_quality', {})
                
                audio_info_data = [
                    ["音频时长", f"{audio_quality.get('duration', 0):.2f} 秒"],
                    ["采样率", f"{audio_quality.get('sample_rate', 0)} Hz"],
                    ["声道数", str(audio_quality.get('channels', 0))],
                    ["音频质量评分", f"{audio_quality.get('quality_score', 0):.1f}/100"],
                    ["识别语言", transcription.get('language', 'unknown')],
                    ["转录文本长度", f"{len(transcription.get('text', ''))} 字符"]
                ]
                audio_info = [[Paragraph(str(cell), self._get_chinese_style('Normal')) for cell in row] for row in audio_info_data]
                
                audio_table = Table(audio_info, colWidths=[2*inch, 4*inch])
                audio_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, -1), 'MSYH'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(audio_table)
                story.append(Spacer(1, 20))
                
                # 音频分段转录表格
                segments = transcription.get('segments', [])
                if segments:
                    story.append(Paragraph("音频分段转录", self._get_chinese_style('Heading2')))
                    story.append(Spacer(1, 12))
                    header = [["序号", "起始时间", "结束时间", "文本"]]
                    seg_table_data = [[Paragraph(str(cell), self._get_chinese_style('Normal', fontSize=8, alignment=TA_CENTER)) for cell in row] for row in header]
                    
                    for idx, seg in enumerate(segments):
                        start = f"{seg.get('start', 0):.2f}s"
                        end = f"{seg.get('end', 0):.2f}s"
                        text = seg.get('text', '')
                        
                        row_data = [
                            Paragraph(str(idx+1), self._get_chinese_style('Normal', fontSize=8, alignment=TA_LEFT)),
                            Paragraph(start, self._get_chinese_style('Normal', fontSize=8, alignment=TA_LEFT)),
                            Paragraph(end, self._get_chinese_style('Normal', fontSize=8, alignment=TA_LEFT)),
                            Paragraph(text, self._get_chinese_style('Normal', fontSize=8, alignment=TA_LEFT))
                        ]
                        seg_table_data.append(row_data)

                    seg_table = Table(seg_table_data, colWidths=[0.5*inch, 0.8*inch, 0.8*inch, 3.9*inch])
                    seg_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('FONTNAME', (0, 0), (-1, -1), 'MSYH'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(seg_table)
                    story.append(Spacer(1, 20))
            
            # 帧分析详情（前10帧）
            story.append(Paragraph("帧分析详情（前10帧）", self._get_chinese_style('Heading2')))
            story.append(Spacer(1, 12))
            
            frame_analyses = result.get('frame_analyses', [])
            if frame_analyses:
                # 准备表格数据
                header = [["帧号", "时间戳", "清晰度", "光照", "人脸", "水印", "内容丰富度", "综合评分"]]
                table_data = [[Paragraph(str(cell), self._get_chinese_style('Normal', fontSize=8, alignment=TA_CENTER)) for cell in row] for row in header]
                
                for frame in frame_analyses[:10]:  # 只显示前10帧
                    row_data = [
                        str(frame.get('frame_number', 0)),
                        f"{frame.get('timestamp', 0):.2f}s",
                        f"{frame.get('clarity_score', 0):.1f}",
                        f"{frame.get('lighting_score', 0):.1f}",
                        "是" if frame.get('face_detected', False) else "否",
                        "是" if frame.get('watermark_detected', False) else "否",
                        f"{frame.get('content_richness', 0):.1f}",
                        f"{frame.get('overall_score', 0):.1f}"
                    ]
                    table_data.append([Paragraph(cell, self._get_chinese_style('Normal', fontSize=8, alignment=TA_CENTER)) for cell in row_data])
                
                frame_table = Table(table_data, colWidths=[0.5*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.5*inch, 0.5*inch, 0.8*inch, 0.7*inch])
                frame_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, -1), 'MSYH'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(frame_table)
            
            # 生成PDF
            doc.build(story)
            logger.info(f"PDF报告已生成: {file_path}")
            
        except Exception as e:
            logger.error(f"生成PDF报告失败: {str(e)}")
            raise
    
    def generate_excel_report(self, result: Dict[str, Any], file_path: str):
        """生成Excel报告"""
        try:
            # 创建Excel写入器
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                
                # 基本信息工作表
                basic_data = {
                    '项目': ['视频名称', '视频时长(秒)', '总帧数', '分析帧数', '综合质量评分'],
                    '数值': [
                        result.get('video_name', 'N/A'),
                        f"{result.get('duration', 0):.2f}",
                        result.get('total_frames', 0),
                        result.get('analyzed_frames', 0),
                        f"{result.get('overall_quality_score', 0):.1f}/100"
                    ]
                }
                basic_df = pd.DataFrame(basic_data)
                basic_df.to_excel(writer, sheet_name='基本信息', index=False)
                
                # 分析摘要工作表
                summary = result.get('summary', {})
                summary_data = {
                    '指标': ['平均清晰度', '平均光照质量', '人脸检测率', '水印检测率', '平均内容丰富度', '音频质量评分', '音频转录状态'],
                    '数值': [
                        f"{summary.get('avg_clarity', 0):.1f}/100",
                        f"{summary.get('avg_lighting', 0):.1f}/100",
                        f"{summary.get('face_detection_rate', 0)*100:.1f}%",
                        f"{summary.get('watermark_detection_rate', 0)*100:.1f}%",
                        f"{summary.get('avg_content_richness', 0):.1f}/100",
                        f"{summary.get('audio_quality_score', 0):.1f}/100",
                        "有转录" if summary.get('has_audio_transcription', False) else "无转录"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='分析摘要', index=False)
                
                # 音频分析工作表
                audio_analysis = result.get('audio_analysis', {})
                if audio_analysis.get('success', False):
                    transcription = audio_analysis.get('transcription', {})
                    audio_quality = audio_analysis.get('audio_quality', {})
                    
                    # 音频基本信息
                    audio_basic_data = {
                        '项目': ['音频时长(秒)', '采样率(Hz)', '声道数', '音频质量评分', '识别语言', '转录文本长度(字符)'],
                        '数值': [
                            f"{audio_quality.get('duration', 0):.2f}",
                            audio_quality.get('sample_rate', 0),
                            audio_quality.get('channels', 0),
                            f"{audio_quality.get('quality_score', 0):.1f}/100",
                            transcription.get('language', 'unknown'),
                            len(transcription.get('text', ''))
                        ]
                    }
                    audio_basic_df = pd.DataFrame(audio_basic_data)
                    audio_basic_df.to_excel(writer, sheet_name='音频分析', index=False)
                    
                    # 音频转录内容
                    if transcription.get('text'):
                        transcription_data = {
                            '转录内容': [transcription.get('text', '')]
                        }
                        transcription_df = pd.DataFrame(transcription_data)
                        transcription_df.to_excel(writer, sheet_name='音频转录', index=False)
                    
                    # 音频分段转录
                    segments = transcription.get('segments', [])
                    if segments:
                        seg_data = []
                        for idx, seg in enumerate(segments):
                            seg_data.append({
                                '序号': idx+1,
                                '起始时间': f"{seg.get('start', 0):.2f}s",
                                '结束时间': f"{seg.get('end', 0):.2f}s",
                                '文本': seg.get('text', '')
                            })
                        seg_df = pd.DataFrame(seg_data)
                        seg_df.to_excel(writer, sheet_name='音频分段转录', index=False)
                    
                    # 音频质量详情
                    volume_stats = audio_quality.get('volume_stats', {})
                    audio_detail_data = {
                        '项目': ['最小音量', '最大音量', '平均音量', 'RMS音量', '动态范围(dB)', '音频问题'],
                        '数值': [
                            volume_stats.get('min', 0),
                            volume_stats.get('max', 0),
                            f"{volume_stats.get('mean', 0):.1f}",
                            f"{volume_stats.get('rms', 0):.1f}",
                            f"{audio_quality.get('dynamic_range', 0):.1f}",
                            ', '.join(audio_quality.get('issues', []))
                        ]
                    }
                    audio_detail_df = pd.DataFrame(audio_detail_data)
                    audio_detail_df.to_excel(writer, sheet_name='音频质量详情', index=False)
                else:
                    # 音频分析失败
                    audio_error_data = {
                        '项目': ['音频分析状态'],
                        '数值': [audio_analysis.get('error', '视频中无音频轨道或音频分析失败')]
                    }
                    audio_error_df = pd.DataFrame(audio_error_data)
                    audio_error_df.to_excel(writer, sheet_name='音频分析', index=False)
                
                # 帧分析详情工作表
                frame_analyses = result.get('frame_analyses', [])
                if frame_analyses:
                    frame_data = []
                    for frame in frame_analyses:
                        frame_data.append({
                            '帧号': frame.get('frame_number', 0),
                            '时间戳(秒)': f"{frame.get('timestamp', 0):.2f}",
                            '清晰度评分': frame.get('clarity_score', 0),
                            '光照评分': frame.get('lighting_score', 0),
                            '人脸检测': '是' if frame.get('face_detected', False) else '否',
                            '人脸数量': frame.get('face_count', 0),
                            '水印检测': '是' if frame.get('watermark_detected', False) else '否',
                            '水印文字': frame.get('watermark_text', ''),
                            '内容丰富度': frame.get('content_richness', 0),
                            '综合评分': frame.get('overall_score', 0),
                            '问题': ', '.join(frame.get('issues', []))
                        })
                    
                    frame_df = pd.DataFrame(frame_data)
                    frame_df.to_excel(writer, sheet_name='帧分析详情', index=False)
                
                # 问题统计工作表
                all_issues = []
                for frame in frame_analyses:
                    all_issues.extend(frame.get('issues', []))
                
                if all_issues:
                    issue_counts = pd.Series(all_issues).value_counts()
                    issue_df = pd.DataFrame({
                        '问题类型': issue_counts.index,
                        '出现次数': issue_counts.values,
                        '出现频率': (issue_counts.values / len(frame_analyses) * 100).round(1)
                    })
                    issue_df.to_excel(writer, sheet_name='问题统计', index=False)
            
            logger.info(f"Excel报告已生成: {file_path}")
            
        except Exception as e:
            logger.error(f"生成Excel报告失败: {str(e)}")
            raise 