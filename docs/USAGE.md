# 使用指南 / Usage Guide

## 图形界面版本 / GUI Version

### 启动程序
```bash
python gui_main.py
```

### 基本操作
1. **选择音频设备** - 从下拉菜单选择音频输入设备
2. **选择翻译方向** - 英译中或中译英
3. **选择模型质量** - 快速/平衡/准确三种模式
4. **开始翻译** - 点击开始按钮开始实时翻译
5. **查看结果** - 在文本框中查看识别和翻译结果

### 高级设置
- **强制CPU模式** - 在GPU不兼容时使用
- **调整录音间隔** - 根据需要调整音频捕获间隔
- **设置最小音频长度** - 过滤过短的音频片段

## 命令行版本 / Command Line Version

### 启动程序
```bash
python main.py
```

### 配置选项
编辑main.py中的配置变量：
```python
SAMPLE_RATE = 16000      # 采样率
INTERVAL = 5             # 录音间隔(秒)
OVERLAP = 1              # 重叠时间(秒)
MODEL_SIZE = "small"     # 模型大小
FORCE_CPU = False        # 强制CPU模式
TRANSLATION_MODE = "en_to_zh"  # 翻译方向
```

## 文本翻译版本 / Text Translation Version

### 启动程序
```bash
python text_translator.py
```

### 功能特点
- 纯文本翻译，无需音频设备
- 支持多种翻译引擎
- 轻量级，启动快速
- 支持批量翻译

## 性能优化建议 / Performance Tips

### GPU加速
- 确保安装了CUDA版本的PyTorch
- 检查GPU兼容性
- 监控GPU内存使用

### 音频质量
- 使用高质量音频设备
- 确保环境安静
- 调整录音音量

### 翻译质量
- 选择合适的Whisper模型大小
- 根据语言选择合适的翻译引擎
- 调整翻译参数

## 故障排除 / Troubleshooting

### 常见错误
1. **模型加载失败** - 检查网络连接和磁盘空间
2. **音频设备错误** - 检查设备连接和权限
3. **翻译失败** - 检查网络连接和API配置
4. **GPU不兼容** - 程序会自动切换到CPU模式

### 日志查看
程序运行时会输出详细日志，帮助诊断问题。
