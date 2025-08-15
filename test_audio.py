import soundcard as sc
import numpy as np
import time

def test_audio_devices():
    """测试音频设备检测功能"""
    print("=== 音频设备测试 ===")
    
    print("\n1. 检测所有扬声器:")
    try:
        speakers = sc.all_speakers()
        for i, speaker in enumerate(speakers):
            print(f"  {i+1}. {speaker.name}")
    except Exception as e:
        print(f"  错误: {e}")
    
    print("\n2. 检测所有麦克风（包括回环设备）:")
    try:
        mics = sc.all_microphones(include_loopback=True)
        for i, mic in enumerate(mics):
            device_type = "回环设备" if "loopback" in mic.name.lower() else "麦克风"
            print(f"  {i+1}. [{device_type}] {mic.name}")
    except Exception as e:
        print(f"  错误: {e}")
    
    print("\n3. 检测默认扬声器:")
    try:
        default_speaker = sc.default_speaker()
        print(f"  默认扬声器: {default_speaker.name}")
        
        # 尝试获取默认扬声器的回环设备
        try:
            loopback_device = sc.get_microphone(default_speaker.name, include_loopback=True)
            print(f"  回环设备: {loopback_device.name}")
        except Exception as e:
            print(f"  回环设备获取失败: {e}")
            
    except Exception as e:
        print(f"  错误: {e}")
    
    print("\n4. 检测默认麦克风:")
    try:
        default_mic = sc.default_microphone()
        print(f"  默认麦克风: {default_mic.name}")
    except Exception as e:
        print(f"  错误: {e}")

def test_audio_recording():
    """测试音频录制功能"""
    print("\n=== 音频录制测试 ===")
    
    try:
        # 尝试使用默认扬声器的回环设备
        default_speaker = sc.default_speaker()
        loopback_device = sc.get_microphone(default_speaker.name, include_loopback=True)
        
        print(f"使用设备: {loopback_device.name}")
        print("开始录制 3 秒音频...")
        
        with loopback_device.recorder(samplerate=16000) as recorder:
            data = recorder.record(numframes=16000 * 3)  # 3 seconds
            
        print(f"录制完成！")
        print(f"音频数据形状: {data.shape}")
        print(f"音频数据类型: {data.dtype}")
        print(f"音频数据范围: {data.min():.4f} ~ {data.max():.4f}")
        print(f"音频数据均值: {data.mean():.4f}")
        
        # 检查是否有有效的音频数据
        if np.abs(data).max() > 0.001:
            print("✓ 检测到有效的音频信号")
        else:
            print("⚠ 音频信号很弱或无信号")
            
    except Exception as e:
        print(f"录制测试失败: {e}")
        
        # 尝试备用方案
        print("\n尝试使用其他设备...")
        try:
            mics = sc.all_microphones(include_loopback=True)
            for mic in mics:
                if "loopback" in mic.name.lower() or "stereo mix" in mic.name.lower():
                    print(f"尝试使用: {mic.name}")
                    with mic.recorder(samplerate=16000) as recorder:
                        data = recorder.record(numframes=16000 * 1)  # 1 second test
                    print(f"✓ 成功使用 {mic.name}")
                    break
            else:
                print("未找到可用的回环设备")
        except Exception as e2:
            print(f"备用方案也失败: {e2}")

def main():
    print("实时音频翻译工具 - 设备测试")
    print("=" * 40)
    
    test_audio_devices()
    
    input("\n按回车键继续音频录制测试...")
    test_audio_recording()
    
    print("\n测试完成！")
    print("\n如果看到有效的音频信号，说明系统音频捕获功能正常。")
    print("如果没有检测到信号，请检查:")
    print("1. 系统是否正在播放音频")
    print("2. 是否启用了立体声混音或安装了虚拟音频线缆")
    print("3. 音频设备权限设置")

if __name__ == "__main__":
    main()