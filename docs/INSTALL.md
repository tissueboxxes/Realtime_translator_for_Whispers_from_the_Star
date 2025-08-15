# 安装指南 / Installation Guide

## 系统要求 / System Requirements

### 最低要求 / Minimum Requirements
- Python 3.8+
- Windows 10/11
- 4GB RAM
- 2GB 可用磁盘空间

### 推荐配置 / Recommended
- Python 3.10+
- Windows 11
- 8GB+ RAM
- NVIDIA GPU (CUDA 11.8+)
- 5GB+ 可用磁盘空间

## 安装步骤 / Installation Steps

### 1. 安装Python

从 [Python官网](https://www.python.org/downloads/) 下载并安装Python 3.8+

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/realtime-translator.git
cd realtime-translator
```

### 3. 创建虚拟环境 (推荐)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 测试安装

```bash
python test_audio.py
```

## 常见问题 / Troubleshooting

### Q: 安装torch时出错
A: 请根据你的CUDA版本安装对应的torch版本：
```bash
# CPU版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Q: 无法识别音频设备
A: 请确保：
1. 音频设备正常工作
2. 安装了soundcard库
3. 运行程序时选择正确的音频设备

### Q: Whisper模型下载失败
A: 请检查网络连接，或手动下载模型文件到缓存目录
