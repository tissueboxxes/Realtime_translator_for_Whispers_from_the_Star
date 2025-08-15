#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成翻译工具
同时包含实时音频翻译和文本翻译功能
"""

import soundcard as sc
import numpy as np
import whisper
import torch
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False
    print("警告: argostranslate未安装，将使用备用翻译方案")

class IntegratedTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("集成翻译工具 - Integrated Translator")
        self.root.geometry("1000x700")
        
        # 音频翻译相关配置
        self.SAMPLE_RATE = 16000
        self.INTERVAL = 5
        self.OVERLAP = 1
        self.MODEL_SIZE = tk.StringVar(value="small")
        self.FORCE_CPU = False
        self.MIN_AUDIO_LENGTH = 1.0
        self.AUDIO_TRANSLATION_MODE = "en_to_zh"
        
        # 设备兼容性检测
        self.device_type = self.detect_optimal_device()
        self.available_models = ["tiny", "base", "small", "medium", "large"]
        
        # 翻译模型选择
        self.translation_model_type = tk.StringVar(value="balanced")  # fast, balanced, accurate
        
        # 音频翻译状态变量
        self.is_audio_running = False
        self.model = None
        self.audio_device = None
        self.translation_queue = queue.Queue()
        self.audio_buffer = np.array([], dtype=np.float32)
        
        # 文本翻译模式
        self.text_translation_mode = tk.StringVar(value="zh_to_en")
        
        # 初始化离线翻译
        self.translation_ready = False
        
        self.setup_ui()
        self.initialize_model()
        self.initialize_offline_translation()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="集成翻译工具", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 创建选项卡
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 音频翻译选项卡
        self.audio_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.audio_frame, text="实时音频翻译")
        
        # 文本翻译选项卡
        self.text_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.text_frame, text="文本翻译")
        
        # 设置音频翻译界面
        self.setup_audio_ui()
        
        # 设置文本翻译界面
        self.setup_text_ui()
        
    def setup_audio_ui(self):
        """设置音频翻译界面"""
        # 控制框架
        control_frame = ttk.Frame(self.audio_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 开始/停止按钮
        self.audio_start_button = ttk.Button(control_frame, text="开始音频翻译", command=self.toggle_audio_translation)
        self.audio_start_button.grid(row=0, column=0, padx=(0, 10))
        
        # 状态标签
        self.audio_status_label = ttk.Label(control_frame, text="状态: 未开始")
        self.audio_status_label.grid(row=0, column=1)
        
        # 翻译模式选择
        mode_frame = ttk.Frame(self.audio_frame)
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(mode_frame, text="翻译模式:").grid(row=0, column=0, padx=(0, 10))
        self.audio_mode_var = tk.StringVar(value="en_to_zh")
        audio_mode_combo = ttk.Combobox(mode_frame, textvariable=self.audio_mode_var, state="readonly", width=20)
        audio_mode_combo['values'] = ("en_to_zh (英文转中文)", "zh_to_en (中文转英文)")
        audio_mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        audio_mode_combo.bind('<<ComboboxSelected>>', self.on_audio_mode_change)
        
        # Whisper模型选择
        model_frame = ttk.Frame(self.audio_frame)
        model_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(model_frame, text="Whisper模型:").grid(row=0, column=0, padx=(0, 10))
        model_combo = ttk.Combobox(model_frame, textvariable=self.MODEL_SIZE, state="readonly", width=15)
        model_combo['values'] = tuple(self.available_models)
        model_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(model_frame, text="翻译质量:").grid(row=0, column=2, padx=(0, 10))
        translation_combo = ttk.Combobox(model_frame, textvariable=self.translation_model_type, state="readonly", width=15)
        translation_combo['values'] = ("fast (快速)", "balanced (平衡)", "accurate (精确)")
        translation_combo.grid(row=0, column=3)
        
        # 音频设备选择
        device_frame = ttk.Frame(self.audio_frame)
        device_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(device_frame, text="音频设备:").grid(row=0, column=0, padx=(0, 10))
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, state="readonly")
        self.device_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 刷新设备按钮
        refresh_button = ttk.Button(device_frame, text="刷新设备", command=self.refresh_devices)
        refresh_button.grid(row=0, column=2, padx=(10, 0))
        
        # 翻译显示区域
        display_frame = ttk.Frame(self.audio_frame)
        display_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # 源文本
        self.audio_source_label = ttk.Label(display_frame, text="英文原文:", font=("Arial", 12, "bold"))
        self.audio_source_label.grid(row=0, column=0, sticky=tk.W)
        self.audio_source_text = scrolledtext.ScrolledText(display_frame, height=8, wrap=tk.WORD, font=("Arial", 11))
        self.audio_source_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
        
        # 目标文本
        self.audio_target_label = ttk.Label(display_frame, text="中文翻译:", font=("Arial", 12, "bold"))
        self.audio_target_label.grid(row=2, column=0, sticky=tk.W)
        self.audio_target_text = scrolledtext.ScrolledText(display_frame, height=8, wrap=tk.WORD, font=("Arial", 11))
        self.audio_target_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.audio_frame.columnconfigure(0, weight=1)
        self.audio_frame.rowconfigure(4, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        device_frame.columnconfigure(1, weight=1)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(1, weight=1)
        display_frame.rowconfigure(3, weight=1)
        
        # 初始化设备
        self.refresh_devices()
        
    def setup_text_ui(self):
        """设置文本翻译界面"""
        # 配置网格权重
        self.text_frame.columnconfigure(1, weight=1)
        self.text_frame.rowconfigure(2, weight=1)
        self.text_frame.rowconfigure(5, weight=1)
        
        # 翻译选项框架
        options_frame = ttk.Frame(self.text_frame)
        options_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)
        
        # 翻译模式选择
        ttk.Label(options_frame, text="翻译模式:").grid(row=0, column=0, padx=(0, 10))
        mode_combo = ttk.Combobox(options_frame, textvariable=self.text_translation_mode, 
                                 values=["zh_to_en", "en_to_zh"], state="readonly", width=15)
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        mode_combo.bind("<<ComboboxSelected>>", self.on_text_mode_change)
        
        # 翻译质量选择
        ttk.Label(options_frame, text="翻译质量:").grid(row=0, column=2, padx=(0, 10))
        text_quality_combo = ttk.Combobox(options_frame, textvariable=self.translation_model_type, 
                                         values=["fast (快速)", "balanced (平衡)", "accurate (精确)"], 
                                         state="readonly", width=15)
        text_quality_combo.grid(row=0, column=3, sticky=tk.W)
        
        # 输入文本区域
        self.text_input_label = ttk.Label(self.text_frame, text="中文输入:", font=("Arial", 12, "bold"))
        self.text_input_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.text_input_text = scrolledtext.ScrolledText(self.text_frame, height=10, wrap=tk.WORD, font=("Arial", 11))
        self.text_input_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 翻译按钮
        translate_btn = ttk.Button(self.text_frame, text="翻译", command=self.translate_text)
        translate_btn.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # 输出文本区域
        self.text_output_label = ttk.Label(self.text_frame, text="英文翻译:", font=("Arial", 12, "bold"))
        self.text_output_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.text_output_text = scrolledtext.ScrolledText(self.text_frame, height=10, wrap=tk.WORD, font=("Arial", 11), state=tk.DISABLED)
        self.text_output_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.text_status_var = tk.StringVar(value="就绪")
        text_status_label = ttk.Label(self.text_frame, textvariable=self.text_status_var, relief=tk.SUNKEN)
        text_status_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 初始化界面标签
        self.update_text_labels()
        
    def on_audio_mode_change(self, event=None):
        """处理音频翻译模式切换"""
        mode_value = self.audio_mode_var.get()
        if "en_to_zh" in mode_value:
            self.AUDIO_TRANSLATION_MODE = "en_to_zh"
            self.audio_source_label.config(text="英文原文:")
            self.audio_target_label.config(text="中文翻译:")
        else:
            self.AUDIO_TRANSLATION_MODE = "zh_to_en"
            self.audio_source_label.config(text="中文原文:")
            self.audio_target_label.config(text="英文翻译:")
        
        # 清空文本区域
        self.audio_source_text.delete(1.0, tk.END)
        self.audio_target_text.delete(1.0, tk.END)
        
    def on_text_mode_change(self, event=None):
        """文本翻译模式改变时的回调函数"""
        self.update_text_labels()
        # 清空文本区域
        self.text_input_text.delete(1.0, tk.END)
        self.text_output_text.config(state=tk.NORMAL)
        self.text_output_text.delete(1.0, tk.END)
        self.text_output_text.config(state=tk.DISABLED)
        
    def update_text_labels(self):
        """根据翻译模式更新文本翻译界面标签"""
        if self.text_translation_mode.get() == "zh_to_en":
            self.text_input_label.config(text="中文输入:")
            self.text_output_label.config(text="英文翻译:")
        else:
            self.text_input_label.config(text="英文输入:")
            self.text_output_label.config(text="中文翻译:")
            
    def detect_optimal_device(self):
        """检测最优设备类型"""
        try:
            if torch.cuda.is_available() and not self.FORCE_CPU:
                # 检查GPU内存
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"检测到GPU，显存: {gpu_memory:.1f}GB")
                if gpu_memory >= 4.0:  # 4GB以上显存推荐使用GPU
                    return "cuda"
                else:
                    print("GPU显存不足，切换到CPU模式")
                    return "cpu"
            else:
                print("未检测到CUDA或强制使用CPU")
                return "cpu"
        except Exception as e:
            print(f"设备检测失败，使用CPU: {e}")
            return "cpu"
    
    def initialize_model(self):
        """初始化Whisper模型"""
        try:
            self.audio_status_label.config(text="状态: 正在加载模型...")
            self.root.update()
            
            print(f"使用设备: {self.device_type}")
            
            # 根据设备类型调整模型大小
            model_size = self.MODEL_SIZE.get()
            if self.device_type == "cpu" and model_size in ["large", "medium"]:
                print(f"CPU模式下将{model_size}模型降级为small以提高性能")
                model_size = "small"
                self.MODEL_SIZE.set("small")
            
            # 加载模型
            self.model = whisper.load_model(model_size, device=self.device_type)
            print(f"已加载 {model_size} 模型")
            
            self.audio_status_label.config(text=f"状态: 模型加载完成 ({self.device_type.upper()})")
            
        except Exception as e:
            error_msg = f"模型加载失败: {str(e)}"
            print(error_msg)
            self.audio_status_label.config(text=f"状态: {error_msg}")
            
    def refresh_devices(self):
        """刷新音频设备列表"""
        try:
            # 获取所有音频设备
            devices = sc.all_microphones(include_loopback=True)
            device_names = []
            
            for i, device in enumerate(devices):
                device_name = device.name
                if hasattr(device, 'isloopback') and device.isloopback:
                    device_name += " (系统音频)"
                device_names.append(f"{i}: {device_name}")
            
            # 更新下拉框
            self.device_combo['values'] = device_names
            
            # 默认选择第一个设备
            if device_names:
                self.device_combo.current(0)
                
        except Exception as e:
            print(f"刷新设备失败: {e}")
            self.device_combo['values'] = ["无可用设备"]
            
    def get_selected_device(self):
        """获取选中的音频设备"""
        try:
            device_str = self.device_var.get()
            if not device_str or device_str == "无可用设备":
                return None
                
            # 提取设备索引
            device_index = int(device_str.split(':')[0])
            devices = sc.all_microphones(include_loopback=True)
            
            if 0 <= device_index < len(devices):
                return devices[device_index]
            return None
            
        except Exception as e:
            print(f"获取设备失败: {e}")
            return None
            
    def toggle_audio_translation(self):
        """切换音频翻译状态"""
        if self.is_audio_running:
            self.stop_audio_translation()
        else:
            self.start_audio_translation()
            
    def start_audio_translation(self):
        """开始音频翻译"""
        if not self.model:
            messagebox.showerror("错误", "模型未加载")
            return
            
        self.audio_device = self.get_selected_device()
        if not self.audio_device:
            messagebox.showerror("错误", "请选择音频设备")
            return
            
        self.is_audio_running = True
        self.audio_start_button.config(text="停止音频翻译")
        self.audio_status_label.config(text="状态: 正在翻译...")
        
        # 清空文本区域
        self.audio_source_text.delete(1.0, tk.END)
        self.audio_target_text.delete(1.0, tk.END)
        
        # 启动翻译线程
        self.translation_thread = threading.Thread(target=self.audio_translation_worker, daemon=True)
        self.translation_thread.start()
        
        # 启动UI更新
        self.update_audio_ui()
        
    def stop_audio_translation(self):
        """停止音频翻译"""
        self.is_audio_running = False
        self.audio_start_button.config(text="开始音频翻译")
        self.audio_status_label.config(text="状态: 已停止")
        
    def audio_translation_worker(self):
        """音频翻译工作线程"""
        try:
            with self.audio_device.recorder(samplerate=self.SAMPLE_RATE, channels=1) as recorder:
                print(f"开始录制音频，设备: {self.audio_device.name}")
                
                while self.is_audio_running:
                    # 录制音频
                    audio_data = recorder.record(numframes=int(self.SAMPLE_RATE * self.INTERVAL))
                    audio_np = audio_data.flatten().astype(np.float32)
                    
                    # 添加到缓冲区
                    self.audio_buffer = np.concatenate([self.audio_buffer, audio_np])
                    
                    # 保持缓冲区大小
                    max_buffer_size = int(self.SAMPLE_RATE * (self.INTERVAL + self.OVERLAP))
                    if len(self.audio_buffer) > max_buffer_size:
                        self.audio_buffer = self.audio_buffer[-max_buffer_size:]
                    
                    # 检查音频长度
                    if len(self.audio_buffer) < int(self.SAMPLE_RATE * self.MIN_AUDIO_LENGTH):
                        continue
                    
                    # 转录音频
                    try:
                        if self.AUDIO_TRANSLATION_MODE == "en_to_zh":
                            # 英文转中文模式
                            result = self.model.transcribe(
                                self.audio_buffer,
                                language='en',
                                initial_prompt="This is English speech for translation."
                            )
                        else:
                            # 中文转英文模式
                            result = self.model.transcribe(
                                self.audio_buffer,
                                language='zh',
                                initial_prompt="这是中文语音，需要转录。"
                            )
                        
                        source_text = result['text'].strip()
                        
                        # 过滤短文本
                        if self.AUDIO_TRANSLATION_MODE == "en_to_zh":
                            if len(source_text) <= 3:
                                continue
                        else:
                            if len(source_text) <= 1:
                                continue
                        
                        # 翻译文本
                        target_text = self.translate_with_quality_mode(source_text, self.AUDIO_TRANSLATION_MODE)
                        
                        # 将结果放入队列
                        self.translation_queue.put((source_text, target_text))
                        
                    except Exception as e:
                        print(f"转录或翻译错误: {e}")
                        continue
                        
        except Exception as e:
            print(f"音频录制错误: {e}")
            self.translation_queue.put(("错误", f"音频录制失败: {str(e)}"))
            
    def update_audio_ui(self):
        """更新音频翻译UI"""
        try:
            while not self.translation_queue.empty():
                source_text, target_text = self.translation_queue.get_nowait()
                
                # 更新源文本
                self.audio_source_text.insert(tk.END, source_text + "\n\n")
                self.audio_source_text.see(tk.END)
                
                # 更新目标文本
                self.audio_target_text.insert(tk.END, target_text + "\n\n")
                self.audio_target_text.see(tk.END)
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"UI更新错误: {e}")
            
        # 如果还在运行，继续更新
        if self.is_audio_running:
            self.root.after(100, self.update_audio_ui)
            
    def translate_text(self):
        """翻译文本"""
        input_text = self.text_input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("警告", "请输入要翻译的文本")
            return
            
        # 在新线程中执行翻译，避免界面卡顿
        threading.Thread(target=self._text_translate_worker, args=(input_text,), daemon=True).start()
        
    def initialize_offline_translation(self):
        """初始化离线翻译模型"""
        if not ARGOS_AVAILABLE:
            self.translation_ready = False
            return
            
        try:
            # 更新包索引
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # 检查并安装中英翻译包
            zh_to_en_installed = False
            en_to_zh_installed = False
            
            installed_packages = argostranslate.package.get_installed_packages()
            for package in installed_packages:
                if package.from_code == "zh" and package.to_code == "en":
                    zh_to_en_installed = True
                elif package.from_code == "en" and package.to_code == "zh":
                    en_to_zh_installed = True
            
            # 安装缺失的翻译包
            for package in available_packages:
                if package.from_code == "zh" and package.to_code == "en" and not zh_to_en_installed:
                    print("正在下载中文到英文翻译模型...")
                    argostranslate.package.install_from_path(package.download())
                    zh_to_en_installed = True
                elif package.from_code == "en" and package.to_code == "zh" and not en_to_zh_installed:
                    print("正在下载英文到中文翻译模型...")
                    argostranslate.package.install_from_path(package.download())
                    en_to_zh_installed = True
            
            self.translation_ready = zh_to_en_installed and en_to_zh_installed
            if self.translation_ready:
                print("离线翻译模型初始化完成")
            else:
                print("警告: 部分翻译模型未能安装")
                
        except Exception as e:
            print(f"离线翻译初始化失败: {e}")
            self.translation_ready = False
    
    def translate_with_quality_mode(self, text, mode):
        """根据质量模式翻译文本"""
        try:
            quality = self.translation_model_type.get().split()[0]  # 提取质量级别
            
            # 根据质量模式选择不同的翻译策略
            if quality == "fast":
                # 快速模式：直接翻译
                if mode == "en_to_zh":
                    if self.translation_ready:
                        return argostranslate.translate.translate(text, "en", "zh")
                    else:
                        return f"[快速翻译] {text}"  # 备用方案
                else:
                    if self.translation_ready:
                        return argostranslate.translate.translate(text, "zh", "en")
                    else:
                        return f"[Fast Translation] {text}"  # 备用方案
            
            elif quality == "balanced":
                # 平衡模式：分句翻译
                sentences = self.split_sentences(text)
                translated_sentences = []
                
                for sentence in sentences:
                    if mode == "en_to_zh":
                        if self.translation_ready:
                            translated = argostranslate.translate.translate(sentence.strip(), "en", "zh")
                        else:
                            translated = f"[平衡翻译] {sentence.strip()}"
                    else:
                        if self.translation_ready:
                            translated = argostranslate.translate.translate(sentence.strip(), "zh", "en")
                        else:
                            translated = f"[Balanced Translation] {sentence.strip()}"
                    translated_sentences.append(translated)
                
                return " ".join(translated_sentences)
            
            else:  # accurate
                # 精确模式：多次翻译取最佳结果
                if self.translation_ready:
                    if mode == "en_to_zh":
                        result1 = argostranslate.translate.translate(text, "en", "zh")
                        # 可以添加更多翻译引擎的结果进行比较
                        return result1
                    else:
                        result1 = argostranslate.translate.translate(text, "zh", "en")
                        return result1
                else:
                    return f"[精确翻译] {text}" if mode == "en_to_zh" else f"[Accurate Translation] {text}"
                    
        except Exception as e:
            print(f"翻译错误: {e}")
            return f"翻译失败: {text}"
    
    def split_sentences(self, text):
        """分割句子"""
        import re
        # 简单的句子分割
        sentences = re.split(r'[.!?。！？]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _text_translate_worker(self, text):
        """文本翻译工作线程"""
        try:
            self.text_status_var.set("翻译中...")
            
            # 使用新的翻译方法
            mode = self.text_translation_mode.get()
            translated = self.translate_with_quality_mode(text, mode)
            
            # 更新输出文本区域
            self.root.after(0, self._update_text_output, translated)
            self.root.after(0, lambda: self.text_status_var.set("翻译完成"))
            
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            self.root.after(0, lambda: self.text_status_var.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            
    def _update_text_output(self, translated_text):
        """更新文本输出区域"""
        self.text_output_text.config(state=tk.NORMAL)
        self.text_output_text.delete(1.0, tk.END)
        self.text_output_text.insert(1.0, translated_text)
        self.text_output_text.config(state=tk.DISABLED)
        
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    print("启动集成翻译工具...")
    app = IntegratedTranslator()
    app.run()

if __name__ == "__main__":
    main()