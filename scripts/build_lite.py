#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级打包脚本 - 只打包文本翻译工具
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_lite_spec():
    """创建轻量级PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['text_translator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'argostranslate',
        'argostranslate.package',
        'argostranslate.translate',
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
        'whisper',
        'torch',
        'torchvision',
        'torchaudio',
        'soundcard',
        'numpy',
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
    name='TextTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('text_translator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建轻量级PyInstaller规格文件")

def install_lite_requirements():
    """安装轻量级依赖"""
    print("正在安装轻量级依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "argostranslate"], check=True)

def build_lite_executable():
    """构建轻量级可执行文件"""
    print("正在构建轻量级可执行文件...")
    
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "text_translator.spec"]
    
    try:
        subprocess.run(cmd, check=True)
        print("轻量级构建完成！")
        
        exe_path = Path("dist/TextTranslator.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"轻量级可执行文件大小: {size_mb:.1f} MB")
            print(f"可执行文件位置: {exe_path.absolute()}")
        else:
            print("警告: 未找到生成的轻量级可执行文件")
            
    except subprocess.CalledProcessError as e:
        print(f"轻量级构建失败: {e}")
        return False
    
    return True

def create_lite_package():
    """创建轻量级便携式包"""
    print("正在创建轻量级便携式包...")
    
    release_dir = Path("release_lite")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制轻量级可执行文件
    exe_src = Path("dist/TextTranslator.exe")
    if exe_src.exists():
        shutil.copy2(exe_src, release_dir / "TextTranslator.exe")
    
    # 复制完整版可执行文件（如果存在）
    full_exe_src = Path("dist/RealTimeTranslator.exe")
    if full_exe_src.exists():
        shutil.copy2(full_exe_src, release_dir / "RealTimeTranslator.exe")
    
    # 创建使用说明
    usage_content = '''
# 翻译工具使用说明

## 文件说明
- `TextTranslator.exe`: 轻量级文本翻译工具（约50MB）
- `RealTimeTranslator.exe`: 完整版实时翻译工具（约3GB，包含语音识别）

## 推荐使用
- 如果只需要文本翻译，使用 TextTranslator.exe
- 如果需要语音翻译，使用 RealTimeTranslator.exe

## 功能对比
| 功能 | TextTranslator | RealTimeTranslator |
|------|----------------|--------------------|
| 文本翻译 | ✅ | ✅ |
| 语音翻译 | ❌ | ✅ |
| 文件大小 | ~50MB | ~3GB |
| 启动速度 | 快 | 慢 |

## 首次使用
首次运行时会自动下载翻译模型（约100MB），请确保网络连接正常。
'''
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print(f"轻量级便携式包已创建: {release_dir.absolute()}")
    
    total_size = sum(f.stat().st_size for f in release_dir.rglob('*') if f.is_file())
    print(f"轻量级包大小: {total_size / (1024 * 1024):.1f} MB")

def main():
    """主函数"""
    print("=== 轻量级翻译工具打包脚本 ===")
    
    try:
        # 1. 安装轻量级依赖
        install_lite_requirements()
        
        # 2. 创建轻量级规格文件
        create_lite_spec()
        
        # 3. 构建轻量级可执行文件
        if build_lite_executable():
            # 4. 创建轻量级便携式包
            create_lite_package()
            print("\n✅ 轻量级打包完成！")
            print("📁 轻量级可执行文件位于 release_lite/ 目录")
        else:
            print("❌ 轻量级打包失败")
            
    except Exception as e:
        print(f"❌ 轻量级打包过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())