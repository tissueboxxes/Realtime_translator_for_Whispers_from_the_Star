# 项目结构说明 / Project Structure

## 文件说明 / File Description

### 核心程序文件 / Core Program Files

- **main.py** - 命令行版本的主程序，支持实时音频翻译
- **gui_main.py** - 图形界面版本，提供用户友好的GUI界面
- **text_translator.py** - 纯文本翻译器，不需要音频输入
- **simple_translator.py** - 简化版翻译器，功能精简
- **integrated_translator.py** - 集成版翻译器，整合多种功能
- **start.py** - 通用启动脚本
- **test_audio.py** - 音频设备测试工具

### 构建脚本 / Build Scripts

位于 `scripts/` 目录下：

- **build_exe.py** - 构建完整版可执行文件 (~3GB)
- **build_optimized_full.py** - 构建优化完整版 (~800MB) ⭐ 推荐
- **build_lite.py** - 构建轻量版 (~40MB)
- **build_simple.py** - 构建简化版 (~40MB)
- **build_minimal.py** - 构建最小版 (~40MB)

### 配置文件 / Configuration Files

- **requirements.txt** - Python依赖包列表
- **config/config_example.json** - 配置文件示例
- **.gitignore** - Git忽略文件列表

### 文档 / Documentation

- **README.md** - 项目主文档
- **docs/INSTALL.md** - 安装指南
- **docs/USAGE.md** - 使用指南

## 版本特性对比 / Version Feature Comparison

| 文件 | 功能 | 大小 | 依赖 | 适用场景 |
|------|------|------|------|----------|
| gui_main.py | 完整GUI | 大 | 完整 | 日常使用 |
| main.py | 命令行 | 大 | 完整 | 开发调试 |
| text_translator.py | 文本翻译 | 小 | 精简 | 轻量使用 |
| simple_translator.py | 简化GUI | 小 | 最少 | 基础需求 |

## 开发建议 / Development Recommendations

### 新功能开发
1. 在对应的核心文件中添加功能
2. 更新相关的构建脚本
3. 更新文档和配置示例
4. 测试所有版本的兼容性

### 性能优化
1. 优先优化核心算法
2. 减少不必要的依赖
3. 使用异步处理提升响应速度
4. 优化内存使用

### 打包优化
1. 使用build_optimized_full.py作为主要打包方案
2. 根据需要调整排除的模块列表
3. 测试不同环境下的兼容性
4. 监控打包后的文件大小
