'''
Author       : Leon Lee
Date         : 2026-05-20 05:37:58
LastEditors  : Leon
LastEditTime : 2026-07-18 23:09:09
Description  : 用python实现把文本文件转换为语音文件
FilePath     : /tts/edge_tts_gui_pyqt.py
'''
"""
Edge TTS GUI - PyQt6 版本
基于 PyQt6 的现代化文本转语音界面
"""

from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QFileDialog, QCheckBox, QScrollArea, QFrame,
                             QSplitter, QTextEdit, QProgressBar, QMessageBox,
                             QDialog, QComboBox, QGroupBox, QGridLayout,
                             QButtonGroup, QRadioButton, QListWidget, QListWidgetItem)
import edge_tts
import subprocess
import asyncio
import json
import glob
import sys
import os
from tts_core import convert_text_to_speech


# 尝试导入 pygame 用于音频播放
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class EdgeTTSAppPyQt(QMainWindow):
    """Edge TTS PyQt6 主窗口"""

    def __init__(self):
        super().__init__()

        # 配色方案
        self.colors = {
            'bg': '#1e1e1e',
            'card': '#2d2d2d',
            'primary': '#0078d4',
            'text': '#e0e0e0',
            'secondary_text': '#a0a0a0',
            'border': '#404040',
            'success': '#16c60c',
            'warning': '#ffb900',
            'danger': '#e81123'
        }

        # 数据
        self.text_files = []
        self.file_checkboxes = []
        self.output_files = []
        self.output_file_names = []
        self.current_text_file = None

        # 语音配置（使用预定义的语音列表）
        self.voices = {
            '晓晓 (女声)': 'zh-CN-XiaoxiaoNeural',
            '晓伊 (女声)': 'zh-CN-XiaoyiNeural',
            '云健 (男声)': 'zh-CN-YunjianNeural',
            '云希 (男声)': 'zh-CN-YunxiNeural',
            '云夏 (男声)': 'zh-CN-YunxiaNeural',
            '云阳 (男声)': 'zh-CN-YunyangNeural',
            '小北 (辽宁方言)': 'zh-CN-liaoning-XiaobeiNeural',
            '小妮 (陕西方言)': 'zh-CN-shaanxi-XiaoniNeural',
        }

        # 设置变量（先设置默认值，后面会被加载的配置覆盖）
        self.voice_var = '晓晓 (女声)'
        self.rate_var = 'normal'
        self.volume_var = 'normal'
        self.output_dir_var = os.getcwd()
        self.format_var = 'mp3'

        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'settings.json')

        # 加载保存的设置
        self.load_settings()

        # 播放相关
        self.play_process = None
        self.is_playing = False
        self.current_audio_file = None
        self.output_files = []  # 存储输出文件路径

        # 初始化 pygame mixer（用于后台播放）
        if HAS_PYGAME:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Pygame mixer 初始化失败: {e}")

        # 播放状态检查定时器
        self.play_check_timer = QTimer(self)
        self.play_check_timer.timeout.connect(self._check_play_status)
        self.play_check_timer.start(1000)

        # 设置窗口
        self.setup_ui()
        self.apply_dark_theme()

    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("Edge TTS - 文本转语音 (PyQt6)")
        self.setGeometry(100, 100, 750, 650)
        self.setMinimumSize(680, 550)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 标题栏
        self.setup_title_bar(main_layout)

        # 内容区域（水平分割）
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(5)

        # 左侧面板
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)

        # 中间面板
        middle_panel = self.create_middle_panel()
        content_splitter.addWidget(middle_panel)

        content_splitter.setSizes([280, 500])
        main_layout.addWidget(content_splitter, 1)

        # 底部面板
        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel)

    def load_settings(self):
        """加载保存的设置"""
        if not os.path.exists(self.config_file):
            # 如果没有配置文件，输出目录默认为当前工作目录
            self.output_dir_var = os.getcwd()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 加载语音设置
            if 'voice' in config and config['voice'] in self.voices:
                self.voice_var = config['voice']

            # 加载语速设置
            if 'rate' in config:
                self.rate_var = config['rate']

            # 加载音量设置
            if 'volume' in config:
                self.volume_var = config['volume']

            # 加载输出目录
            if 'output_dir' in config and os.path.exists(config['output_dir']):
                self.output_dir_var = config['output_dir']
            else:
                # 如果配置的输出目录不存在，使用当前工作目录
                self.output_dir_var = os.getcwd()

            # 加载输出格式
            if 'format' in config:
                self.format_var = config['format']

        except Exception as e:
            print(f"加载设置失败: {e}")
            self.output_dir_var = os.getcwd()

    def save_settings_to_file(self):
        """保存设置到文件"""
        try:
            config = {
                'voice': self.voice_var,
                'rate': self.rate_var,
                'volume': self.volume_var,
                'output_dir': self.output_dir_var,
                'format': self.format_var
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存设置失败: {e}")

    def apply_dark_theme(self):
        """应用暗色主题"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['bg']};
            }}
            QWidget {{
                background-color: {self.colors['bg']};
                color: {self.colors['text']};
            }}
            QFrame#titleFrame {{
                background-color: {self.colors['card']};
                border: 1px solid {self.colors['border']};
                border-radius: 5px;
            }}
            QLabel {{
                color: {self.colors['text']};
            }}
            QLineEdit {{
                background-color: {self.colors['bg']};
                color: white;
                border: 1px solid {self.colors['border']};
                border-radius: 3px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.colors['primary']};
            }}
        """)

    def setup_title_bar(self, parent_layout):
        """设置标题栏"""
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        # 标题
        title_label = QLabel("Edge TTS - 文本转语音")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0078d4;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setFont(QFont("Microsoft YaHei", 10))
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.show_settings_dialog)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        title_layout.addWidget(settings_btn)

        parent_layout.addWidget(title_frame)

    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        # 输入文件列表标题
        input_title = QLabel("输入文件列表")
        input_title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        input_title.setStyleSheet("color: #0078d4; padding: 5px;")
        left_layout.addWidget(input_title)

        # 全选按钮和计数
        select_frame = QFrame()
        select_layout = QHBoxLayout(select_frame)
        select_layout.setContentsMargins(5, 5, 5, 5)

        self.select_all_btn = QPushButton("取消全选")
        self.select_all_btn.setFont(QFont("Microsoft YaHei", 9))
        self.select_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        select_layout.addWidget(self.select_all_btn)

        self.selected_count_label = QLabel("已选: 0")
        self.selected_count_label.setFont(QFont("Microsoft YaHei", 9))
        self.selected_count_label.setStyleSheet(
            "color: #e0e0e0; padding-left: 10px;")
        select_layout.addWidget(self.selected_count_label)
        select_layout.addStretch()

        left_layout.addWidget(select_frame)

        # 目录选择
        dir_frame = QFrame()
        dir_layout = QHBoxLayout(dir_frame)
        dir_layout.setContentsMargins(5, 5, 5, 5)

        self.dir_entry = QLineEdit()
        self.dir_entry.setFont(QFont("Microsoft YaHei", 9))
        self.dir_entry.setPlaceholderText("请选择文本文件目录...")
        dir_layout.addWidget(self.dir_entry)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setFont(QFont("Microsoft YaHei", 9))
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_file_list)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #16c60c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #13a00a;
            }
        """)
        dir_layout.addWidget(refresh_btn)

        browse_btn = QPushButton("📂 浏览")
        browse_btn.setFont(QFont("Microsoft YaHei", 9))
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self.browse_directory)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        dir_layout.addWidget(browse_btn)

        left_layout.addWidget(dir_frame)

        # 文件列表（滚动区域）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #2d2d2d;
            }
        """)

        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_container)
        self.checkbox_layout.setContentsMargins(5, 5, 5, 5)
        self.checkbox_layout.addStretch()

        self.scroll_area.setWidget(self.checkbox_container)
        left_layout.addWidget(self.scroll_area, 1)

        # 输出文件列表
        output_title = QLabel("输出文件列表:")
        output_title.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        output_title.setStyleSheet("color: #0078d4; padding: 5px;")
        left_layout.addWidget(output_title)

        # 播放提示
        self.play_hint_label = QLabel("(点击文件播放)")
        self.play_hint_label.setFont(QFont("Microsoft YaHei", 8))
        self.play_hint_label.setStyleSheet("color: #808080; padding: 2px 5px;")
        left_layout.addWidget(self.play_hint_label)

        self.output_list = QListWidget()
        self.output_list.setFont(QFont("Microsoft YaHei", 9))
        self.output_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        self.output_list.itemClicked.connect(self.on_output_file_clicked)
        left_layout.addWidget(self.output_list, 1)

        return left_widget

    def create_middle_panel(self):
        """创建中间面板"""
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        preview_title = QLabel("📄 文本预览")
        preview_title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        preview_title.setStyleSheet("color: #0078d4; padding: 5px;")
        middle_layout.addWidget(preview_title)

        # 统计信息
        self.stats_label = QLabel("未选择文件 | 字数: 0 | 预计时长: 0秒")
        self.stats_label.setFont(QFont("Microsoft YaHei", 9))
        self.stats_label.setStyleSheet("color: #0078d4; padding: 5px;")
        middle_layout.addWidget(self.stats_label)

        # 预览文本框
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Microsoft YaHei", 10))
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #1e1e1e;
                color: #e0e0e0;
                padding: 10px;
            }
        """)
        middle_layout.addWidget(self.preview_text, 1)

        return middle_widget

    def create_bottom_panel(self):
        """创建底部面板"""
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 10, 0, 0)
        bottom_layout.setSpacing(15)

        # 按钮区域
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # 开始转换按钮
        self.convert_btn = QPushButton(" 开始转换")
        self.convert_btn.setFont(
            QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                border: 2px solid #16a34a;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QPushButton:pressed {
                background-color: #15803d;
            }
        """)
        button_layout.addWidget(self.convert_btn)

        # 播放按钮
        self.play_btn = QPushButton("▶️ 播放音频")
        self.play_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setEnabled(False)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: 2px solid #d97706;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
            QPushButton:pressed {
                background-color: #b45309;
            }
            QPushButton:disabled {
                background-color: #6b7280;
                border-color: #4b5563;
            }
        """)
        button_layout.addWidget(self.play_btn)

        # 打开文件夹按钮
        open_folder_btn = QPushButton("📁 打开文件夹")
        open_folder_btn.setFont(
            QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_folder_btn.clicked.connect(self.open_output_folder)
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: 2px solid #2563eb;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        button_layout.addWidget(open_folder_btn)

        button_layout.addStretch()

        # 进度条区域
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(3)

        progress_label = QLabel("转换进度:")
        progress_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        progress_label.setStyleSheet("color: #e0e0e0;")
        progress_layout.addWidget(progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(250)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #2d2d2d;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        # 第一行：按钮和进度条水平排列
        top_row = QFrame()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(15)
        top_row_layout.addWidget(button_frame)
        top_row_layout.addWidget(progress_frame)
        top_row_layout.addStretch()

        bottom_layout.addWidget(top_row)

        # 第二行：状态文字（在按钮下方）
        self.progress_info_label = QLabel("00:00 / 00:00")
        self.progress_info_label.setFont(QFont("Microsoft YaHei", 9))
        self.progress_info_label.setStyleSheet("color: #e0e0e0;")
        self.progress_info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bottom_layout.addWidget(self.progress_info_label)

        return bottom_widget

    def toggle_select_all(self):
        """全选/取消全选"""
        if not self.file_checkboxes:
            return

        # 检查是否全部选中
        all_checked = all(cb.isChecked() for cb in self.file_checkboxes)

        # 切换状态
        new_state = not all_checked
        for cb in self.file_checkboxes:
            cb.setChecked(new_state)

        # 更新按钮文本
        self.select_all_btn.setText("取消全选" if new_state else "全选")
        self.update_selected_count()

    def refresh_file_list(self):
        """刷新文件列表"""
        directory = self.dir_entry.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self, "提示", "请选择有效的文本目录")
            return

        # 清空列表
        self.text_files = []
        self.file_checkboxes = []

        # 清除旧的复选框（保留stretch项）
        while self.checkbox_layout.count() > 1:
            child = self.checkbox_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 扫描文件
        txt_files = glob.glob(os.path.join(directory, "*.txt"))
        txt_files.sort()

        # 创建复选框
        for filepath in txt_files:
            filename = os.path.basename(filepath)
            self.text_files.append(filepath)

            checkbox = QCheckBox(filename)
            checkbox.setFont(QFont("Microsoft YaHei", 10))
            checkbox.setChecked(True)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:checked {
                    background-color: #0078d4;
                    border: 1px solid #0078d4;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                }
            """)
            checkbox.stateChanged.connect(self.update_selected_count)
            checkbox.clicked.connect(
                lambda checked, fp=filepath: self.preview_text_file(fp))

            # 插入到拉伸项之前
            self.checkbox_layout.insertWidget(
                self.checkbox_layout.count() - 1, checkbox)
            self.file_checkboxes.append(checkbox)

        self.update_selected_count()

    def preview_text_file(self, filepath):
        """预览文本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            self.preview_text.setPlainText(content)
            self.current_text_file = filepath

            # 更新统计信息
            char_count = len(content)
            # 假设每秒约 15 个字符（正常语速）
            duration_seconds = char_count / 15
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)

            self.stats_label.setText(
                f"字数: {char_count} | 预计时长: {minutes:02d}:{seconds:02d}"
            )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"读取文件失败: {str(e)}")

    def update_selected_count(self):
        """更新选中计数"""
        count = sum(1 for cb in self.file_checkboxes if cb.isChecked())
        self.selected_count_label.setText(f"已选: {count}")

    def browse_directory(self):
        """浏览目录"""
        directory = self._get_directory("选择文本目录")
        if directory:
            self.dir_entry.setText(directory)
            self.output_dir_var = directory
            self.refresh_file_list()

    def _get_directory(self, title):
        """跨平台目录选择"""
        import os
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            directory = filedialog.askdirectory(title=title)
            root.destroy()
            return directory if directory else None
        except Exception as e:
            QMessageBox.warning(self, "错误", f"选择目录失败: {str(e)}")
            return None

    def show_settings_dialog(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def start_conversion(self):
        """开始转换"""
        # 获取选中的文件
        selected_files = [
            self.text_files[i] for i, cb in enumerate(self.file_checkboxes)
            if cb.isChecked()
        ]

        if not selected_files:
            QMessageBox.warning(self, "提示", "请至少选择一个文件")
            return

        # 禁用转换按钮
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText(" 转换中...")

        # 重置进度条
        self.progress_bar.setValue(0)
        self.progress_info_label.setText(f"0 / {len(selected_files)}")

        # 在后台线程中执行转换
        self.conversion_thread = ConversionThread(
            selected_files,
            self.voices[self.voice_var],
            self.rate_var,
            self.volume_var,
            self.output_dir_var,
            self.format_var
        )
        self.conversion_thread.progress.connect(self.update_progress)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.error.connect(self.conversion_error)
        self.conversion_thread.start()

        self.status_var = "正在转换..."

    def update_progress(self, current, total, filename):
        """更新进度"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_info_label.setText(f"{current} / {total} - {filename}")

    def conversion_finished(self, output_files):
        """转换完成"""
        self.output_files = output_files
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText(" 开始转换")
        self.progress_bar.setValue(100)
        self.progress_info_label.setText(f"完成! 共 {len(output_files)} 个文件")

        # 更新输出文件列表显示
        self.update_output_list()

        # 启用播放按钮
        if output_files:
            self.play_btn.setEnabled(True)
            self.current_audio_file = output_files[0]

        QMessageBox.information(
            self, "成功",
            f"转换完成!\n共生成 {len(output_files)} 个音频文件"
        )

    def update_output_list(self):
        """更新输出文件列表显示"""
        self.output_list.clear()

        if not self.output_files:
            self.output_list.addItem("暂无输出文件")
            self.play_hint_label.setVisible(False)
            return

        self.play_hint_label.setVisible(True)

        # 添加文件到列表
        for idx, filepath in enumerate(self.output_files):
            filename = os.path.basename(filepath)
            item = QListWidgetItem(f"{idx+1}. {filename}")
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            self.output_list.addItem(item)

        # 默认选中第一个文件
        if self.output_files:
            self.output_list.setCurrentRow(0)
            self.current_audio_file = self.output_files[0]

    def on_output_file_clicked(self, item):
        """点击输出文件列表项"""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if filepath and os.path.exists(filepath):
            self.current_audio_file = filepath
            # 如果正在播放，先停止
            if self.is_playing:
                self.toggle_playback()
            # 然后播放新文件
            self.toggle_playback()

    def conversion_error(self, error_msg):
        """转换错误"""
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText(" 开始转换")
        QMessageBox.critical(self, "错误", f"转换失败:\n{error_msg}")

    def toggle_playback(self):
        """切换播放"""
        if not self.current_audio_file:
            QMessageBox.warning(self, "提示", "请先转换音频文件")
            return

        if not os.path.exists(self.current_audio_file):
            QMessageBox.warning(self, "提示", "音频文件不存在")
            return

        if self.is_playing:
            # 停止播放
            stopped = False

            if self.play_process:
                # 子进程播放器（ffplay, vlc, mpv 等）
                try:
                    self.play_process.terminate()
                    self.play_process.wait(timeout=2)
                    self.play_process = None
                    stopped = True
                    print("已停止子进程播放器")
                except Exception as e:
                    print(f"停止子进程失败: {e}")

            if not stopped and HAS_PYGAME and pygame.mixer.get_init():
                # pygame 播放器
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                        # 重要：清理资源
                        pygame.mixer.music.unload()
                        stopped = True
                        print("已停止 pygame 播放器")
                except Exception as e:
                    print(f"停止 pygame 失败: {e}")

            # 注意：winsound 无法中途停止，只能等播放完毕
            if not stopped:
                print("警告：当前播放器不支持中途停止")

            self.is_playing = False
            self.play_btn.setText("▶️ 播放音频")
            self.progress_info_label.setText("已停止")
        else:
            # 开始播放 - 使用后台播放器
            try:
                player = None

                # 按优先级检测可用的播放器
                if sys.platform == 'win32':
                    # Windows: 优先使用 ffplay, vlc, mpv
                    for cmd in ['ffplay', 'vlc', 'mpv']:
                        if self._check_command_exists(cmd):
                            player = cmd
                            break

                    if player == 'ffplay':
                        # ffplay 后台播放，不显示窗口
                        self.play_process = subprocess.Popen(
                            ['ffplay', '-nodisp', '-autoexit',
                                self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    elif player == 'vlc':
                        # VLC 后台播放
                        self.play_process = subprocess.Popen(
                            ['vlc', '--play-and-exit', '--intf',
                                'dummy', self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    elif player == 'mpv':
                        # mpv 无界面播放
                        self.play_process = subprocess.Popen(
                            ['mpv', '--no-video', '--no-terminal',
                                self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    else:
                        # 后备方案：使用 pygame 或系统播放器
                        audio_path = os.path.abspath(self.current_audio_file)

                        if not os.path.exists(audio_path):
                            QMessageBox.critical(
                                self, "错误",
                                f"音频文件不存在:\n{audio_path}")
                            return

                        if HAS_PYGAME:
                            # 使用 pygame 后台播放（优先于 winsound）
                            try:
                                pygame.mixer.music.load(audio_path)
                                pygame.mixer.music.play()
                                self.is_playing = True
                                self.play_btn.setText("⏹️ 停止播放")
                                self.progress_info_label.setText(
                                    "正在播放... (pygame)")
                                print(f"pygame 开始播放: {audio_path}")
                                return  # pygame 播放成功，直接返回
                            except Exception as e:
                                print(f"pygame 播放失败: {e}")

                        # 最后的后备方案：winsound（无法停止）
                        file_ext = os.path.splitext(audio_path)[1].lower()
                        if file_ext == '.wav' and sys.platform == 'win32':
                            # Windows WAV 使用 winsound
                            import winsound
                            try:
                                winsound.PlaySound(
                                    audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                                self.is_playing = True
                                self.play_btn.setText("️ 停止播放")
                                self.progress_info_label.setText(
                                    "正在播放... (winsound - 无法停止)")
                                print(f"winsound 开始播放: {audio_path}")
                                return
                            except Exception as e:
                                print(f"winsound 播放失败: {e}")

                        # 如果以上都失败，使用系统默认播放器（会弹出窗口）
                        if sys.platform == 'win32':
                            self.play_process = subprocess.Popen(
                                ['start', '', audio_path],
                                shell=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )

                elif sys.platform == 'darwin':
                    # macOS
                    for cmd in ['ffplay', 'vlc', 'mpv', 'afplay']:
                        if self._check_command_exists(cmd):
                            player = cmd
                            break

                    if player == 'ffplay':
                        self.play_process = subprocess.Popen(
                            ['ffplay', '-nodisp', '-autoexit',
                                self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    elif player == 'afplay':
                        # macOS 自带的 afplay
                        self.play_process = subprocess.Popen(
                            ['afplay', self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    else:
                        self.play_process = subprocess.Popen(
                            ['afplay', self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )

                else:
                    # Linux
                    for cmd in ['ffplay', 'vlc', 'mpv', 'paplay']:
                        if self._check_command_exists(cmd):
                            player = cmd
                            break

                    if player == 'ffplay':
                        self.play_process = subprocess.Popen(
                            ['ffplay', '-nodisp', '-autoexit',
                                self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    else:
                        self.play_process = subprocess.Popen(
                            [player or 'paplay', self.current_audio_file],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )

                self.is_playing = True
                self.play_btn.setText("⏹️ 停止播放")
                self.progress_info_label.setText("正在播放...")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"播放失败: {str(e)}")

    def _check_play_status(self):
        """检查播放状态，播放完成后复位"""
        if self.is_playing:
            # 检查子进程播放器
            if self.play_process:
                if self.play_process.poll() is not None:
                    self.play_process = None
                    self._reset_play_state()
                    return

            # 检查 pygame 播放器
            if HAS_PYGAME and pygame.mixer.get_init():
                if not pygame.mixer.music.get_busy():
                    self._reset_play_state()
                    return

    def _reset_play_state(self):
        """复位播放状态"""
        self.is_playing = False
        self.play_btn.setText("▶️ 播放音频")
        self.progress_info_label.setText("已停止")
        self.progress_bar.setValue(0)

    def _check_command_exists(self, cmd):
        """检查命令是否存在"""
        try:
            if sys.platform == 'win32':
                subprocess.run(['where', cmd],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               check=True)
            else:
                subprocess.run(['which', cmd],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               check=True)
            return True
        except:
            return False

    def open_output_folder(self):
        """打开输出文件夹"""
        output_dir = self.output_dir_var
        if not os.path.exists(output_dir):
            QMessageBox.warning(self, "提示", "输出目录不存在")
            return

        # 验证路径安全性，防止路径遍历攻击
        output_dir = os.path.abspath(output_dir)
        if not output_dir.startswith(os.path.abspath(os.getcwd())):
            QMessageBox.warning(self, "提示", "不允许访问外部目录")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', output_dir])
            else:
                subprocess.Popen(['xdg-open', output_dir])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开文件夹失败: {str(e)}")


class ConversionThread(QThread):
    """TTS转换线程"""
    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(list)  # output_files
    error = pyqtSignal(str)  # error_message

    def __init__(self, text_files, voice, rate, volume, output_dir, format_type):
        super().__init__()
        self.text_files = text_files
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.output_dir = output_dir
        self.format_type = format_type

    def run(self):
        """执行转换"""
        try:
            output_files = []
            total = len(self.text_files)

            # 创建输出目录
            os.makedirs(self.output_dir, exist_ok=True)

            for idx, text_file in enumerate(self.text_files):
                filename = os.path.basename(text_file)
                self.progress.emit(idx + 1, total, filename)

                # 读取文本
                with open(text_file, 'r', encoding='utf-8') as f:
                    text = f.read()

                # 生成输出文件名
                base_name = os.path.splitext(filename)[0]
                output_file = os.path.join(
                    self.output_dir,
                    f"{base_name}.{self.format_type}"
                )

                # 处理含 {pause=XXX} 停顿标记的文本，支持重试
                max_retries = 3
                retry_count = 0
                last_error = None

                while retry_count < max_retries:
                    try:
                        asyncio.run(convert_text_to_speech(
                            text, self.voice, self.rate, self.volume, output_file
                        ))
                        output_files.append(output_file)
                        break  # 成功，跳出重试循环

                    except Exception as e:
                        last_error = str(e)
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(2)
                            self.progress.emit(
                                idx + 1, total, f"{filename} (重试 {retry_count}/{max_retries})")
                        else:
                            raise Exception(
                                f"转换失败（已重试{max_retries}次）: {last_error}")

            self.finished.emit(output_files)

        except Exception as e:
            self.error.emit(str(e))

class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("设置")
        self.setFixedSize(550, 480)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background-color: #2d2d2d; }")

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)

        # === 语音设置 ===
        voice_group = QGroupBox("🎙️ 语音设置")
        voice_group.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        voice_group.setStyleSheet(
            "QGroupBox { color: #0078d4; border: 1px solid #404040; border-radius: 5px; padding-top: 15px; }")
        voice_layout = QVBoxLayout(voice_group)

        # 语音选择
        voice_combo_layout = QHBoxLayout()
        voice_combo_layout.addWidget(QLabel("选择语音:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(list(self.parent.voices.keys()))
        if self.parent.voice_var in self.parent.voices:
            self.voice_combo.setCurrentText(self.parent.voice_var)
        else:
            self.voice_combo.setCurrentIndex(0)
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        voice_combo_layout.addWidget(self.voice_combo)
        voice_layout.addLayout(voice_combo_layout)

        # 语速设置
        voice_layout.addWidget(QLabel("语速:"))
        speed_layout = QHBoxLayout()
        self.speed_group = QButtonGroup(self)
        self.speed_normal = QRadioButton("正常")
        self.speed_fast = QRadioButton("加快 (+20%)")
        self.speed_slow = QRadioButton("减慢 (-20%)")

        current_rate = self.parent.rate_var
        self.speed_normal.setChecked(current_rate == 'normal')
        self.speed_fast.setChecked(current_rate == 'fast')
        self.speed_slow.setChecked(current_rate == 'slow')

        self.speed_group.addButton(self.speed_normal, 0)
        self.speed_group.addButton(self.speed_fast, 1)
        self.speed_group.addButton(self.speed_slow, 2)

        speed_layout.addWidget(self.speed_normal)
        speed_layout.addWidget(self.speed_fast)
        speed_layout.addWidget(self.speed_slow)
        voice_layout.addLayout(speed_layout)

        self.speed_normal.clicked.connect(self._on_settings_changed)
        self.speed_fast.clicked.connect(self._on_settings_changed)
        self.speed_slow.clicked.connect(self._on_settings_changed)

        # 音量设置
        voice_layout.addWidget(QLabel("音量:"))
        volume_layout = QHBoxLayout()
        self.volume_group = QButtonGroup(self)
        self.volume_normal = QRadioButton("正常")
        self.volume_loud = QRadioButton("增大 (+20%)")
        self.volume_quiet = QRadioButton("减小 (-20%)")

        current_volume = self.parent.volume_var
        self.volume_normal.setChecked(current_volume == 'normal')
        self.volume_loud.setChecked(current_volume == 'loud')
        self.volume_quiet.setChecked(current_volume == 'quiet')

        self.volume_group.addButton(self.volume_normal, 0)
        self.volume_group.addButton(self.volume_loud, 1)
        self.volume_group.addButton(self.volume_quiet, 2)

        volume_layout.addWidget(self.volume_normal)
        volume_layout.addWidget(self.volume_loud)
        volume_layout.addWidget(self.volume_quiet)
        voice_layout.addLayout(volume_layout)

        self.volume_normal.clicked.connect(self._on_settings_changed)
        self.volume_loud.clicked.connect(self._on_settings_changed)
        self.volume_quiet.clicked.connect(self._on_settings_changed)

        scroll_layout.addWidget(voice_group)

        # === 输出设置 ===
        output_group = QGroupBox("📁 输出设置")
        output_group.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        output_group.setStyleSheet(
            "QGroupBox { color: #0078d4; border: 1px solid #404040; border-radius: 5px; padding-top: 15px; }")
        output_layout = QVBoxLayout(output_group)

        # 输出目录
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("输出目录:"))
        self.output_dir_entry = QLineEdit()
        self.output_dir_entry.setText(self.parent.output_dir_var)
        dir_layout.addWidget(self.output_dir_entry)

        select_dir_btn = QPushButton("📂 选择")
        select_dir_btn.clicked.connect(self.select_output_dir)
        dir_layout.addWidget(select_dir_btn)
        output_layout.addLayout(dir_layout)

        # 输出格式
        output_layout.addWidget(QLabel("输出格式:"))
        format_layout = QHBoxLayout()
        self.format_group = QButtonGroup(self)
        self.format_mp3 = QRadioButton("MP3")
        self.format_wav = QRadioButton("WAV")

        current_format = self.parent.format_var
        self.format_mp3.setChecked(current_format == 'mp3')
        self.format_wav.setChecked(current_format == 'wav')

        self.format_group.addButton(self.format_mp3, 0)
        self.format_group.addButton(self.format_wav, 1)

        format_layout.addWidget(self.format_mp3)
        format_layout.addWidget(self.format_wav)
        format_layout.addStretch()
        output_layout.addLayout(format_layout)

        scroll_layout.addWidget(output_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("✓ 确定")
        ok_btn.clicked.connect(self.save_settings)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #9ca3af;
            }
        """)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def select_output_dir(self):
        """选择输出目录"""
        directory = self.parent._get_directory("选择输出目录")
        if directory:
            self.output_dir_entry.setText(directory)

    def _on_voice_changed(self, index):
        """语音选择变化时自动播放预览"""
        voice_name = self.voice_combo.currentText()
        self._preview_voice(voice_name)

    def _on_settings_changed(self):
        """语速或音量变化时自动播放预览"""
        self._preview_voice()

    def _preview_voice(self, voice_name=None):
        """播放语音预览"""
        try:
            if voice_name is None:
                voice_name = self.voice_combo.currentText()
            
            voice_key = self.parent.voices.get(voice_name)
            if not voice_key:
                print(f"[预览] 未找到语音: {voice_name}")
                return

            preview_text = "你好，这是语音预览。"
            
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_file = f.name

            rate = '+0%'
            if self.speed_fast.isChecked():
                rate = '+20%'
            elif self.speed_slow.isChecked():
                rate = '-20%'

            volume = '+0%'
            if self.volume_loud.isChecked():
                volume = '+20%'
            elif self.volume_quiet.isChecked():
                volume = '-20%'

            print(f"[预览] 正在生成语音: {voice_name} ({voice_key}), 语速: {rate}, 音量: {volume}")
            communicate = edge_tts.Communicate(preview_text, voice_key, rate=rate, volume=volume)
            asyncio.run(communicate.save(temp_file))

            if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 100:
                print(f"[预览] 生成失败，文件太小或不存在: {temp_file}")
                os.unlink(temp_file)
                return

            print(f"[预览] 生成成功，文件大小: {os.path.getsize(temp_file)} bytes")

            player = None
            for cmd in ['ffplay', 'vlc', 'mpv']:
                try:
                    result = subprocess.run(
                        ['which' if sys.platform != 'win32' else 'where', cmd],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        player = cmd
                        break
                except:
                    continue

            if player:
                print(f"[预览] 使用播放器: {player}")
                subprocess.Popen(
                    [player] + (['-nodisp', '-autoexit', temp_file] if player == 'ffplay' else
                                ['--play-and-exit', '--intf', 'dummy', temp_file] if player == 'vlc' else
                                ['--no-video', '--no-terminal', temp_file]),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                print(f"[预览] 使用 pygame")
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()

            def cleanup():
                try:
                    os.unlink(temp_file)
                except:
                    pass

            QTimer.singleShot(5000, cleanup)

        except Exception as e:
            print(f"[预览] 失败: {e}")

    def save_settings(self):
        """保存设置"""
        # 保存语音
        self.parent.voice_var = self.voice_combo.currentText()

        # 保存语速
        if self.speed_normal.isChecked():
            self.parent.rate_var = 'normal'
        elif self.speed_fast.isChecked():
            self.parent.rate_var = 'fast'
        else:
            self.parent.rate_var = 'slow'

        # 保存音量
        if self.volume_normal.isChecked():
            self.parent.volume_var = 'normal'
        elif self.volume_loud.isChecked():
            self.parent.volume_var = 'loud'
        else:
            self.parent.volume_var = 'quiet'

        # 保存输出目录
        self.parent.output_dir_var = self.output_dir_entry.text()

        # 保存输出格式
        if self.format_mp3.isChecked():
            self.parent.format_var = 'mp3'
        else:
            self.parent.format_var = 'wav'

        # 保存设置到文件
        self.parent.save_settings_to_file()

        self.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格

    window = EdgeTTSAppPyQt()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
