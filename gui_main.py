import soundcard as sc
import numpy as np
import whisper
import translators as ts
import torch
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time

class RealtimeTranslationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("实时音频翻译工具 - Realtime Audio Translation")
        self.root.geometry("800x600")
        
        # Configuration
        self.SAMPLE_RATE = 16000
        self.INTERVAL = 5  # seconds - 增加录制间隔以获取更完整的句子
        self.OVERLAP = 1  # seconds - 重叠时间，确保句子不被截断
        self.MODEL_SIZE = "small"  # 使用更准确的模型
        self.FORCE_CPU = False  # 启用GPU模式，提升性能
        self.MIN_AUDIO_LENGTH = 1.0  # 最小音频长度（秒）
        self.TRANSLATION_MODE = "en_to_zh"  # "en_to_zh" (英文转中文) 或 "zh_to_en" (中文转英文)
        
        # State variables
        self.is_running = False
        self.model = None
        self.audio_device = None
        self.translation_queue = queue.Queue()
        self.audio_buffer = np.array([], dtype=np.float32)  # 音频缓冲区
        
        self.setup_ui()
        self.initialize_model()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="实时音频翻译工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Start/Stop button
        self.start_button = ttk.Button(control_frame, text="开始翻译", command=self.toggle_translation)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="状态: 未开始")
        self.status_label.grid(row=0, column=1)
        
        # Translation mode selection
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(mode_frame, text="翻译模式:").grid(row=0, column=0, padx=(0, 10))
        self.mode_var = tk.StringVar(value="en_to_zh")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, state="readonly", width=20)
        mode_combo['values'] = ("en_to_zh (英文转中文)", "zh_to_en (中文转英文)")
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        # Audio device selection
        device_frame = ttk.Frame(main_frame)
        device_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(device_frame, text="音频设备:").grid(row=0, column=0, padx=(0, 10))
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, state="readonly")
        self.device_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Refresh devices button
        refresh_button = ttk.Button(device_frame, text="刷新设备", command=self.refresh_devices)
        refresh_button.grid(row=0, column=2, padx=(10, 0))
        
        # Translation display
        display_frame = ttk.Frame(main_frame)
        display_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Source text (will be updated based on mode)
        self.source_label = ttk.Label(display_frame, text="英文原文:", font=("Arial", 12, "bold"))
        self.source_label.grid(row=0, column=0, sticky=tk.W)
        self.source_text = scrolledtext.ScrolledText(display_frame, height=8, wrap=tk.WORD, font=("Arial", 11))
        self.source_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
        
        # Target text (will be updated based on mode)
        self.target_label = ttk.Label(display_frame, text="中文翻译:", font=("Arial", 12, "bold"))
        self.target_label.grid(row=2, column=0, sticky=tk.W)
        self.target_text = scrolledtext.ScrolledText(display_frame, height=8, wrap=tk.WORD, font=("Arial", 11))
        self.target_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        device_frame.columnconfigure(1, weight=1)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(1, weight=1)
        display_frame.rowconfigure(3, weight=1)
        
        # Initialize devices
        self.refresh_devices()
        
    def on_mode_change(self, event=None):
        """处理翻译模式切换"""
        mode_value = self.mode_var.get()
        if "en_to_zh" in mode_value:
            self.TRANSLATION_MODE = "en_to_zh"
            self.source_label.config(text="英文原文:")
            self.target_label.config(text="中文翻译:")
        else:
            self.TRANSLATION_MODE = "zh_to_en"
            self.source_label.config(text="中文原文:")
            self.target_label.config(text="英文翻译:")
        
        # 清空文本区域
        self.source_text.delete(1.0, tk.END)
        self.target_text.delete(1.0, tk.END)
        
    def initialize_model(self):
        """Initialize Whisper model in a separate thread"""
        def load_model():
            try:
                self.status_label.config(text="状态: 正在加载模型...")
                
                # 设备选择逻辑
                if self.FORCE_CPU:
                    device = "cpu"
                    device_info = "CPU (强制模式)"
                elif torch.cuda.is_available():
                    try:
                        # 测试GPU兼容性
                        test_tensor = torch.tensor([1.0]).cuda()
                        device = "cuda"
                        device_info = "GPU (兼容性测试通过)"
                    except Exception as gpu_error:
                        device = "cpu"
                        device_info = f"CPU (GPU不兼容: {str(gpu_error)[:50]}...)"
                else:
                    device = "cpu"
                    device_info = "CPU (未检测到CUDA)"
                
                self.model = whisper.load_model(self.MODEL_SIZE, device=device)
                self.status_label.config(text=f"状态: 模型加载完成 ({device_info})")
            except Exception as e:
                self.status_label.config(text=f"状态: 模型加载失败 - {str(e)}")
        
        threading.Thread(target=load_model, daemon=True).start()
        
    def refresh_devices(self):
        """Refresh audio device list"""
        try:
            # Get loopback microphones (for system audio)
            loopback_mics = sc.all_microphones(include_loopback=True)
            device_names = []
            
            # Try to get default speaker loopback
            try:
                default_speaker = sc.get_microphone(sc.default_speaker().name, include_loopback=True)
                device_names.append(f"默认扬声器: {default_speaker.name}")
            except:
                pass
            
            # Add other loopback devices
            for mic in loopback_mics:
                if 'loopback' in mic.name.lower() or 'stereo mix' in mic.name.lower():
                    device_names.append(f"回环设备: {mic.name}")
            
            # Add regular microphones as fallback
            regular_mics = sc.all_microphones(include_loopback=False)
            for mic in regular_mics:
                device_names.append(f"麦克风: {mic.name}")
            
            self.device_combo['values'] = device_names
            if device_names:
                self.device_combo.current(0)
                
        except Exception as e:
            self.status_label.config(text=f"状态: 设备刷新失败 - {str(e)}")
    
    def get_selected_device(self):
        """Get the selected audio device"""
        selected = self.device_var.get()
        if not selected:
            return None
            
        try:
            if selected.startswith("默认扬声器:"):
                return sc.get_microphone(sc.default_speaker().name, include_loopback=True)
            elif selected.startswith("回环设备:"):
                device_name = selected.replace("回环设备: ", "")
                return sc.get_microphone(device_name, include_loopback=True)
            elif selected.startswith("麦克风:"):
                device_name = selected.replace("麦克风: ", "")
                return sc.get_microphone(device_name, include_loopback=False)
        except Exception as e:
            print(f"Error getting device: {e}")
            return None
    
    def toggle_translation(self):
        """Start or stop translation"""
        if not self.is_running:
            self.start_translation()
        else:
            self.stop_translation()
    
    def start_translation(self):
        """Start real-time translation"""
        if not self.model:
            self.status_label.config(text="状态: 请等待模型加载完成")
            return
            
        self.audio_device = self.get_selected_device()
        if not self.audio_device:
            self.status_label.config(text="状态: 请选择有效的音频设备")
            return
        
        self.is_running = True
        self.start_button.config(text="停止翻译")
        self.status_label.config(text="状态: 正在翻译...")
        
        # Clear text areas
        self.source_text.delete(1.0, tk.END)
        self.target_text.delete(1.0, tk.END)
        
        # Start translation thread
        self.translation_thread = threading.Thread(target=self.translation_worker, daemon=True)
        self.translation_thread.start()
        
        # Start UI update timer
        self.update_ui()
    
    def stop_translation(self):
        """Stop real-time translation"""
        self.is_running = False
        self.start_button.config(text="开始翻译")
        self.status_label.config(text="状态: 已停止")
    
    def translation_worker(self):
        """Worker thread for audio processing and translation"""
        try:
            # 重置音频缓冲区
            self.audio_buffer = np.array([], dtype=np.float32)
            
            with self.audio_device.recorder(samplerate=self.SAMPLE_RATE, channels=1) as recorder:
                while self.is_running:
                    try:
                        # Record audio
                        data = recorder.record(numframes=self.SAMPLE_RATE * self.INTERVAL)
                        
                        # 检查音频数据质量
                        if len(data) == 0 or np.max(np.abs(data)) < 0.001:
                            continue  # 跳过静音或无效数据
                        
                        # Convert to float32 numpy array
                        current_audio = data.astype(np.float32).flatten()
                        
                        # 音频预处理：音量标准化
                        max_val = np.max(np.abs(current_audio))
                        if max_val > 0:
                            current_audio = current_audio / max_val * 0.8  # 标准化到80%音量
                        
                        # 实现重叠录制：将当前音频与缓冲区合并
                        if len(self.audio_buffer) > 0:
                            # 保留上一段音频的重叠部分
                            overlap_samples = int(self.SAMPLE_RATE * self.OVERLAP)
                            if len(self.audio_buffer) >= overlap_samples:
                                overlap_audio = self.audio_buffer[-overlap_samples:]
                                # 合并重叠音频和当前音频
                                audio_data = np.concatenate([overlap_audio, current_audio])
                            else:
                                audio_data = np.concatenate([self.audio_buffer, current_audio])
                        else:
                            audio_data = current_audio
                        
                        # 更新缓冲区
                        self.audio_buffer = current_audio
                        
                        # 检查音频长度是否足够
                        audio_duration = len(audio_data) / self.SAMPLE_RATE
                        if audio_duration < self.MIN_AUDIO_LENGTH:
                            continue
                        
                        # 根据翻译模式进行转录和翻译
                        if self.TRANSLATION_MODE == "en_to_zh":
                            # 英文转中文模式
                            result = self.model.transcribe(
                                audio_data, 
                                fp16=torch.cuda.is_available(),
                                language='en',  # 明确指定语言为英文
                                task='transcribe',  # 明确指定任务
                                temperature=0.0,  # 降低随机性
                                best_of=1,  # 减少计算量但保持质量
                                beam_size=1,  # 简化beam search
                                patience=1.0,  # 提高耐心等待完整句子
                                length_penalty=1.0,  # 不惩罚长句子
                                suppress_tokens="-1",  # 不抑制任何token
                                initial_prompt="This is a conversation in English."  # 提供上下文提示
                            )
                            source_text = result.get("text", "").strip()
                            
                            if source_text and len(source_text) > 3:  # 过滤过短的转录结果
                                # 翻译为中文
                                try:
                                    target_text = ts.translate_text(source_text, from_language='en', to_language='zh-CN')
                                except Exception as e:
                                    target_text = f"翻译失败: {str(e)}"
                                
                                # Add to queue for UI update
                                timestamp = time.strftime("%H:%M:%S")
                                self.translation_queue.put((timestamp, source_text, target_text))
                                
                        else:
                            # 中文转英文模式
                            result = self.model.transcribe(
                                audio_data, 
                                fp16=torch.cuda.is_available(),
                                language='zh',  # 明确指定语言为中文
                                task='transcribe',  # 明确指定任务
                                temperature=0.0,  # 降低随机性
                                best_of=1,  # 减少计算量但保持质量
                                beam_size=1,  # 简化beam search
                                patience=1.0,  # 提高耐心等待完整句子
                                length_penalty=1.0,  # 不惩罚长句子
                                suppress_tokens="-1",  # 不抑制任何token
                                initial_prompt="这是一段中文对话。"  # 提供中文上下文提示
                            )
                            source_text = result.get("text", "").strip()
                            
                            if source_text and len(source_text) > 1:  # 中文字符较短，调整过滤条件
                                # 翻译为英文
                                try:
                                    target_text = ts.translate_text(source_text, from_language='zh-CN', to_language='en')
                                except Exception as e:
                                    target_text = f"翻译失败: {str(e)}"
                                
                                # Add to queue for UI update
                                timestamp = time.strftime("%H:%M:%S")
                                self.translation_queue.put((timestamp, source_text, target_text))
                            
                    except Exception as e:
                        if self.is_running:  # Only show error if still running
                            self.translation_queue.put(("ERROR", str(e), ""))
                        break
                        
        except Exception as e:
            if self.is_running:
                self.translation_queue.put(("ERROR", f"录音失败: {str(e)}", ""))
    
    def update_ui(self):
        """Update UI with new translations"""
        try:
            while not self.translation_queue.empty():
                timestamp, source, target = self.translation_queue.get_nowait()
                
                if timestamp == "ERROR":
                    self.status_label.config(text=f"状态: 错误 - {source}")
                    self.stop_translation()
                    return
                
                # Add to text areas
                self.source_text.insert(tk.END, f"[{timestamp}] {source}\n\n")
                self.target_text.insert(tk.END, f"[{timestamp}] {target}\n\n")
                
                # Auto-scroll to bottom
                self.source_text.see(tk.END)
                self.target_text.see(tk.END)
                
        except queue.Empty:
            pass
        
        if self.is_running:
            self.root.after(100, self.update_ui)  # Update every 100ms

def main():
    root = tk.Tk()
    app = RealtimeTranslationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()