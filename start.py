#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时音频翻译工具启动器
Realtime Audio Translation Tool Launcher
"""

import os
import sys
import subprocess

def print_banner():
    """打印程序横幅"""
    print("="*60)
    print("    实时音频翻译工具 (Realtime Audio Translation Tool)")
    print("="*60)
    print("    功能: 捕获系统音频 → 英文转录 → 中文翻译")
    print("    技术: OpenAI Whisper + 机器翻译")
    print("="*60)

def check_dependencies():
    """检查依赖包"""
    print("\n检查依赖包...")
    
    required_packages = [
        'soundcard',
        'numpy', 
        'whisper',
        'torch',
        'translators'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'whisper':
                import whisper
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (缺失)")
            missing_packages.append(package)
    
    # 检查GPU兼容性
    try:
        import torch
        if torch.cuda.is_available():
            try:
                test_tensor = torch.tensor([1.0]).cuda()
                print("✓ GPU兼容性测试通过")
            except Exception as e:
                print(f"⚠ GPU不兼容，将使用CPU模式: {str(e)[:50]}...")
        else:
            print("ℹ 未检测到CUDA，将使用CPU模式")
    except ImportError:
        pass
    
    if missing_packages:
        print(f"\n⚠ 发现缺失的依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False
    
    print("\n✓ 所有依赖包已安装")
    return True

def show_menu():
    """显示主菜单"""
    print("\n请选择运行模式:")
    print("1. 图形界面版本 (推荐) - gui_main.py")
    print("2. 命令行版本 - main.py")
    print("3. 音频设备测试 - test_audio.py")
    print("4. 安装/更新依赖包")
    print("5. 查看帮助信息")
    print("0. 退出")
    print("-" * 40)

def install_dependencies():
    """安装依赖包"""
    print("\n正在安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✓ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        return False
    return True

def show_help():
    """显示帮助信息"""
    help_text = """
=== 使用帮助 ===

1. 图形界面版本 (gui_main.py):
   - 提供友好的图形用户界面
   - 实时显示英文转录和中文翻译
   - 支持音频设备选择
   - 显示翻译历史记录
   - 推荐新手使用

2. 命令行版本 (main.py):
   - 在终端中运行
   - 适合服务器环境或自动化场景
   - 资源占用更少

3. 音频设备测试 (test_audio.py):
   - 检测系统音频设备
   - 测试音频捕获功能
   - 排查音频问题

=== 系统音频捕获设置 ===

Windows 系统需要启用音频回环设备:

方法1 - 启用立体声混音:
1. 右键点击系统托盘音量图标
2. 选择"声音设置" → "声音控制面板"
3. 在"录制"选项卡中右键空白处
4. 选择"显示已禁用的设备"
5. 找到"立体声混音"并启用

方法2 - 使用虚拟音频线缆:
1. 下载安装 VB-Audio Virtual Cable
2. 将系统音频输出设置为虚拟线缆
3. 程序从虚拟线缆捕获音频

=== 故障排除 ===

问题1: 无法捕获系统音频
解决: 检查音频回环设备设置

问题2: 模型加载失败
解决: 检查网络连接和磁盘空间

问题3: 翻译失败
解决: 检查网络连接

问题4: 程序运行缓慢
解决: 使用更小的Whisper模型或启用GPU加速

=== 技术参数 ===

- 音频采样率: 16000 Hz
- 处理间隔: 3 秒
- 默认模型: Whisper base
- 翻译方向: 英文 → 中文
"""
    print(help_text)

def run_program(script_name):
    """运行指定的程序"""
    if not os.path.exists(script_name):
        print(f"✗ 文件不存在: {script_name}")
        return
    
    print(f"\n启动 {script_name}...")
    try:
        subprocess.run([sys.executable, script_name])
    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"\n程序运行出错: {e}")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        choice = input("\n是否现在安装依赖包? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            if not install_dependencies():
                print("依赖包安装失败，程序退出")
                return
        else:
            print("请先安装依赖包后再运行程序")
            return
    
    while True:
        show_menu()
        
        try:
            choice = input("请输入选项 (0-5): ").strip()
            
            if choice == '0':
                print("\n再见！")
                break
            elif choice == '1':
                run_program('gui_main.py')
            elif choice == '2':
                run_program('main.py')
            elif choice == '3':
                run_program('test_audio.py')
            elif choice == '4':
                install_dependencies()
            elif choice == '5':
                show_help()
            else:
                print("\n无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n\n程序已退出")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()