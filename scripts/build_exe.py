#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行文件的脚本
使用PyInstaller将翻译工具打包成独立的exe文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """安装必要的依赖"""
    print("正在安装依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['integrated_translator.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
    ],
    hiddenimports=[
        'argostranslate',
        'argostranslate.package',
        'argostranslate.translate',
        'whisper',
        'torch',
        'soundcard',
        'numpy',
        'tkinter',
        'threading',
        'queue',
        'time',
        're'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'PIL',
        'cv2',
        'sklearn',
        'tensorflow',
        'keras',
        'plotly',
        'bokeh',
        'seaborn',
        'statsmodels',
        'sympy',
        'pytest',
        'sphinx',
        'jinja2',
        'babel',
        'docutils'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RealTimeTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('translator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建PyInstaller规格文件")

def build_executable():
    """构建可执行文件"""
    print("正在构建可执行文件...")
    
    # 使用spec文件构建
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "translator.spec"]
    
    try:
        subprocess.run(cmd, check=True)
        print("构建完成！")
        
        # 检查输出文件
        exe_path = Path("dist/RealTimeTranslator.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"可执行文件大小: {size_mb:.1f} MB")
            print(f"可执行文件位置: {exe_path.absolute()}")
        else:
            print("警告: 未找到生成的可执行文件")
            
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False
    
    return True

def create_portable_package():
    """创建便携式包"""
    print("正在创建便携式包...")
    
    # 创建发布目录
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_src = Path("dist/RealTimeTranslator.exe")
    if exe_src.exists():
        shutil.copy2(exe_src, release_dir / "RealTimeTranslator.exe")
    
    # 复制必要文件
    files_to_copy = [
        "README.md",
        "requirements.txt",
        "text_translator.py"
    ]
    
    for file_name in files_to_copy:
        src_file = Path(file_name)
        if src_file.exists():
            shutil.copy2(src_file, release_dir / file_name)
    
    # 创建使用说明
    usage_content = '''
# 实时翻译工具使用说明

## 快速开始
1. 双击 `RealTimeTranslator.exe` 启动集成翻译工具
2. 或者运行 `python text_translator.py` 使用独立文本翻译工具

## 功能特性
- 实时音频翻译（英中互译）
- 文本翻译（支持长句）
- 离线翻译（无需网络）
- 多种翻译质量模式
- CPU/GPU自动适配

## 翻译质量模式
- **快速模式**: 速度优先，适合实时翻译
- **平衡模式**: 速度与质量平衡，推荐日常使用
- **精确模式**: 质量优先，适合重要文档

## 系统要求
- Windows 10/11
- 4GB+ RAM（推荐8GB+）
- 支持CUDA的显卡（可选，用于加速）

## 故障排除
如果遇到问题，请检查：
1. 音频设备是否正常工作
2. 网络连接（首次使用需下载模型）
3. 系统权限（可能需要管理员权限）

## 技术支持
如有问题，请查看控制台输出获取详细错误信息。
'''
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print(f"便携式包已创建: {release_dir.absolute()}")
    
    # 计算总大小
    total_size = sum(f.stat().st_size for f in release_dir.rglob('*') if f.is_file())
    print(f"总包大小: {total_size / (1024 * 1024):.1f} MB")

def main():
    """主函数"""
    print("=== 实时翻译工具打包脚本 ===")
    
    try:
        # 1. 安装依赖
        install_requirements()
        
        # 2. 创建规格文件
        create_spec_file()
        
        # 3. 构建可执行文件
        if build_executable():
            # 4. 创建便携式包
            create_portable_package()
            print("\n✅ 打包完成！")
            print("📁 可执行文件位于 release/ 目录")
        else:
            print("❌ 打包失败")
            
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())