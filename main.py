import soundcard as sc
import numpy as np
import whisper
import translators as ts
import torch
import os
import sys
import time
import threading
import queue

# --- Configuration ---
SAMPLE_RATE = 16000  # Whisper model's required sample rate
INTERVAL = 5  # seconds - 增加录制间隔以获取更完整的句子
OVERLAP = 1  # seconds - 重叠时间，确保句子不被截断
MODEL_SIZE = "small" # "tiny", "base", "small", "medium", "large" - 使用更准确的模型
FORCE_CPU = False  # 启用GPU模式，提升性能
MIN_AUDIO_LENGTH = 1.0  # 最小音频长度（秒），过短的音频片段将被跳过
TRANSLATION_MODE = "en_to_zh"  # "en_to_zh" (英文转中文) 或 "zh_to_en" (中文转英文)

def get_translation_mode():
    """
    让用户选择翻译模式
    """
    print("请选择翻译模式:")
    print("1. 英文转中文 (English to Chinese)")
    print("2. 中文转英文 (Chinese to English)")
    
    while True:
        choice = input("请输入选择 (1 或 2): ").strip()
        if choice == "1":
            return "en_to_zh"
        elif choice == "2":
            return "zh_to_en"
        else:
            print("无效选择，请输入 1 或 2")

def main():
    """
    Main function to capture, transcribe, and translate audio.
    """
    # 获取翻译模式
    global TRANSLATION_MODE
    TRANSLATION_MODE = get_translation_mode()
    # --- Initialization ---
    print("Initializing...")
    
    # Check for GPU with compatibility
    if FORCE_CPU:
        device = "cpu"
        print(f"Using device: {device} (强制使用CPU模式)")
    elif torch.cuda.is_available():
        try:
            # 测试GPU兼容性
            test_tensor = torch.tensor([1.0]).cuda()
            device = "cuda"
            print(f"Using device: {device} (GPU兼容性测试通过)")
        except Exception as e:
            device = "cpu"
            print(f"GPU不兼容，切换到CPU模式: {e}")
    else:
        device = "cpu"
        print(f"Using device: {device} (未检测到CUDA)")

    # Load Whisper model
    print(f"Loading Whisper model ({MODEL_SIZE})...")
    model = whisper.load_model(MODEL_SIZE, device=device)
    
    # Get the default speaker for loopback recording (system audio)
    try:
        default_speaker = sc.get_microphone(sc.default_speaker().name, include_loopback=True)
        print(f"Capturing audio from: {default_speaker.name}")
    except Exception as e:
        print(f"Error getting default speaker loopback: {e}")
        # Fallback: try to find any loopback microphone
        loopback_mics = sc.all_microphones(include_loopback=True)
        loopback_mics = [mic for mic in loopback_mics if 'loopback' in mic.name.lower() or 'stereo mix' in mic.name.lower()]
        if not loopback_mics:
            print("No loopback devices found. Please enable 'Stereo Mix' or similar in your audio settings.")
            return
        default_speaker = loopback_mics[0]
        print(f"Using loopback device: {default_speaker.name}")

    # --- Main Loop ---
    print("\n--- Starting Real-time Translation ---")
    if TRANSLATION_MODE == "en_to_zh":
        print("模式: 英文转中文 - Playing audio on your system. The English transcription and Chinese translation will appear below.")
    else:
        print("模式: 中文转英文 - Playing audio on your system. The Chinese transcription and English translation will appear below.")
    
    # 音频缓冲区用于重叠录制
    audio_buffer = np.array([], dtype=np.float32)
    
    with default_speaker.recorder(samplerate=SAMPLE_RATE, channels=1) as recorder:
        while True:
            try:
                # Record audio from system output for the given interval
                data = recorder.record(numframes=SAMPLE_RATE * INTERVAL)
                
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
                if len(audio_buffer) > 0:
                    # 保留上一段音频的重叠部分
                    overlap_samples = int(SAMPLE_RATE * OVERLAP)
                    if len(audio_buffer) >= overlap_samples:
                        overlap_audio = audio_buffer[-overlap_samples:]
                        # 合并重叠音频和当前音频
                        audio_data = np.concatenate([overlap_audio, current_audio])
                    else:
                        audio_data = np.concatenate([audio_buffer, current_audio])
                else:
                    audio_data = current_audio
                
                # 更新缓冲区
                audio_buffer = current_audio
                
                # 检查音频长度是否足够
                audio_duration = len(audio_data) / SAMPLE_RATE
                if audio_duration < MIN_AUDIO_LENGTH:
                    continue

                # 根据翻译模式进行转录和翻译
                if TRANSLATION_MODE == "en_to_zh":
                    # 英文转中文模式
                    result = model.transcribe(
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
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"\n[{timestamp}] English: {source_text}")
                        
                        # 翻译为中文
                        try:
                            target_text = ts.translate_text(source_text, from_language='en', to_language='zh-CN')
                            print(f"[{timestamp}] Chinese: {target_text}")
                        except Exception as e:
                            print(f"[{timestamp}] 翻译失败: {e}")
                            continue
                            
                else:
                    # 中文转英文模式
                    result = model.transcribe(
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
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"\n[{timestamp}] Chinese: {source_text}")
                        
                        # 翻译为英文
                        try:
                            target_text = ts.translate_text(source_text, from_language='zh-CN', to_language='en')
                            print(f"[{timestamp}] English: {target_text}")
                        except Exception as e:
                            print(f"[{timestamp}] 翻译失败: {e}")
                            continue

            except KeyboardInterrupt:
                print("\n--- Stopping Real-time Translation ---")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

if __name__ == "__main__":
    main()