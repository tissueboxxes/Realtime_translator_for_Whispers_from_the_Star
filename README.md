# 实时音频翻译工具 / Realtime Audio Translation Tool

一个基于Whisper和多种翻译引擎的实时音频翻译工具，支持中英文双向翻译。

A real-time audio translation tool based on Whisper and multiple translation engines, supporting bidirectional Chinese-English translation.

## ✨ 功能特性 / Features

- 🎤 **实时语音识别** - 基于OpenAI Whisper模型的高精度语音识别
- 🌐 **多引擎翻译** - 支持多种翻译引擎（Google、百度、有道等）
- 🔄 **双向翻译** - 支持中英文双向实时翻译
- 🖥️ **图形界面** - 简洁易用的GUI界面
- ⚡ **智能优化** - GPU/CPU自动适配，性能优化
- 📦 **多版本打包** - 提供不同大小和功能的可执行文件

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- Python 3.8+
- Windows 10/11 (主要测试平台)
- 4GB+ RAM
- 可选：NVIDIA GPU (CUDA支持,支持50系列显卡)

### 安装依赖 / Installation

```bash
# 克隆项目
git clone https://github.com/yourusername/realtime-translator.git
cd realtime-translator

# 安装依赖
pip install -r requirements.txt
```

### 运行程序 / Usage

#### 方式1：图形界面版本
```bash
python gui_main.py
```

#### 方式2：命令行版本
```bash
python main.py
```

#### 方式3：文本翻译版本
```bash
python text_translator.py
```

#### 方式4：简化版本
```bash
python simple_translator.py
```

## 📦 打包可执行文件 / Build Executables

项目提供多种打包选项：

### 完整版 (约3GB)
```bash
python scripts/build_exe.py
```

### 优化完整版 (约800MB) ⭐ 推荐
```bash
python scripts/build_optimized_full.py
```

### 文本翻译版 (约40MB)
```bash
python scripts/build_lite.py
```

### 简化版 (约40MB)
```bash
python scripts/build_simple.py
```

### 最小版 (约40MB)
```bash
python scripts/build_minimal.py
```

## 📁 项目结构 / Project Structure

```
realtime-translator/
├── main.py                 # 命令行版本主程序
├── gui_main.py            # GUI版本主程序
├── text_translator.py     # 文本翻译器
├── simple_translator.py   # 简化版翻译器
├── integrated_translator.py # 集成版翻译器
├── start.py              # 启动脚本
├── test_audio.py         # 音频测试工具
├── requirements.txt      # 依赖列表
├── scripts/              # 构建脚本
│   ├── build_exe.py
│   ├── build_optimized_full.py
│   ├── build_lite.py
│   ├── build_simple.py
│   └── build_minimal.py
├── config/               # 配置文件
│   └── config_example.json
├── docs/                 # 文档
│   ├── INSTALL.md
│   ├── USAGE.md
│   └── API.md
└── README.md
```

## 🔧 配置说明 / Configuration

详细配置说明请参考 [配置文档](docs/CONFIG.md)

## 📖 使用指南 / Usage Guide

详细使用指南请参考 [使用文档](docs/USAGE.md)

## 🛠️ 开发指南 / Development

详细开发指南请参考 [开发文档](docs/DEVELOPMENT.md)

## 📋 版本对比 / Version Comparison

| 版本 | 大小 | 功能 | 推荐场景 |
|------|------|------|----------|
| 完整版 | ~3GB | 语音识别+翻译 | 开发测试 |
| 优化完整版 ⭐ | ~800MB | 语音识别+翻译 | 日常使用 |
| 文本翻译版 | ~40MB | 仅文本翻译 | 轻量使用 |
| 简化版 | ~40MB | 仅文本翻译 | 最小安装 |

## 🤝 贡献 / Contributing

欢迎提交Issue和Pull Request！

## 📄 许可证 / License

MIT License

## 🙏 致谢 / Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [Translators](https://github.com/UlionTse/translators) - 翻译引擎
- [ArgosTranslate](https://github.com/argosopentech/argos-translate) - 离线翻译

## 📞 联系 / Contact

如有问题或建议，请提交Issue或联系开发者。

