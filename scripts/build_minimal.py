#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小化打包脚本 - 极致精简版本
通过多种优化策略大幅减小exe文件大小
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_minimal_spec():
    """创建最小化PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['text_translator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'argostranslate.package',
        'argostranslate.translate'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除所有大型机器学习库
        'whisper',
        'torch',
        'torchvision', 
        'torchaudio',
        'transformers',
        'tensorflow',
        'keras',
        'sklearn',
        'scipy',
        'numpy.f2py',
        'numpy.distutils',
        'numpy.testing',
        
        # 排除音频处理库
        'soundcard',
        'pyaudio',
        'wave',
        'audioop',
        
        # 排除图像处理库
        'PIL',
        'cv2',
        'matplotlib',
        'plotly',
        'seaborn',
        'bokeh',
        
        # 排除开发工具
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'sphinx',
        'setuptools',
        'pip',
        'wheel',
        
        # 排除文档和模板库
        'jinja2',
        'babel',
        'docutils',
        'markupsafe',
        
        # 排除网络库
        'urllib3',
        'requests',
        'certifi',
        'charset_normalizer',
        
        # 排除其他不必要的库
        'pandas',
        'sympy',
        'statsmodels',
        'openpyxl',
        'xlrd',
        'lxml',
        'bs4',
        'html5lib',
        
        # 排除测试相关
        'unittest',
        'test',
        'tests',
        
        # 排除编译器相关
        'distutils',
        'compiler',
        'msilib',
        
        # 排除多媒体库
        'pygame',
        'pyglet',
        
        # 排除GUI库（除了tkinter）
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        'kivy'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 进一步过滤，只保留核心模块
a.pure = [x for x in a.pure if not any([
    x[0].startswith('numpy.') and x[0] not in ['numpy', 'numpy.core', 'numpy.lib'],
    x[0].startswith('scipy.'),
    x[0].startswith('matplotlib.'),
    x[0].startswith('PIL.'),
    x[0].startswith('torch.'),
    x[0].startswith('transformers.'),
    x[0].startswith('sklearn.'),
    x[0].startswith('pandas.'),
    x[0].startswith('jupyter.'),
    x[0].startswith('IPython.'),
    x[0].startswith('notebook.'),
    x[0].startswith('test.'),
    x[0].startswith('tests.'),
    x[0].startswith('unittest.'),
    x[0].endswith('_test'),
    x[0].endswith('.test'),
    x[0].endswith('.tests')
])]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TextTranslator_Mini',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用strip减小大小
    upx=True,    # 启用UPX压缩
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
    
    with open('minimal.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建最小化PyInstaller规格文件")

def install_minimal_requirements():
    """安装最小化依赖"""
    print("正在安装最小化依赖...")
    # 只安装核心翻译库
    subprocess.run([sys.executable, "-m", "pip", "install", "argostranslate", "--no-deps"], check=True)
    
def build_minimal_executable():
    """构建最小化可执行文件"""
    print("正在构建最小化可执行文件...")
    
    # 设置环境变量以进一步优化
    env = os.environ.copy()
    env['PYTHONOPTIMIZE'] = '2'  # 启用最高级别优化
    
    cmd = [
        sys.executable, "-m", "PyInstaller", 
        "--clean",
        "minimal.spec"
    ]
    
    try:
        subprocess.run(cmd, check=True, env=env)
        print("最小化构建完成！")
        
        exe_path = Path("dist/TextTranslator_Mini.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"最小化可执行文件大小: {size_mb:.1f} MB")
            print(f"可执行文件位置: {exe_path.absolute()}")
            
            # 尝试使用外部UPX进一步压缩
            try_upx_compression(exe_path)
        else:
            print("警告: 未找到生成的最小化可执行文件")
            
    except subprocess.CalledProcessError as e:
        print(f"最小化构建失败: {e}")
        return False
    
    return True

def try_upx_compression(exe_path):
    """尝试使用UPX压缩"""
    try:
        # 检查是否有UPX
        subprocess.run(["upx", "--version"], capture_output=True, check=True)
        
        print("正在使用UPX压缩...")
        original_size = exe_path.stat().st_size
        
        # 创建备份
        backup_path = exe_path.with_suffix('.exe.backup')
        shutil.copy2(exe_path, backup_path)
        
        # 使用UPX压缩
        subprocess.run(["upx", "--best", "--lzma", str(exe_path)], check=True)
        
        compressed_size = exe_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"UPX压缩完成！压缩率: {compression_ratio:.1f}%")
        print(f"压缩后大小: {compressed_size / (1024 * 1024):.1f} MB")
        
        # 删除备份
        backup_path.unlink()
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("UPX不可用，跳过压缩步骤")

def create_minimal_package():
    """创建最小化便携式包"""
    print("正在创建最小化便携式包...")
    
    release_dir = Path("release_minimal")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制最小化可执行文件
    exe_src = Path("dist/TextTranslator_Mini.exe")
    if exe_src.exists():
        shutil.copy2(exe_src, release_dir / "TextTranslator_Mini.exe")
    
    # 创建使用说明
    usage_content = '''
# 最小化文本翻译工具

## 版本说明
这是极致精简版本的文本翻译工具，专注于核心翻译功能。

## 功能特性
- ✅ 中英文双向翻译
- ✅ 离线运行（首次需联网下载模型）
- ✅ 轻量级设计
- ❌ 不支持语音翻译
- ❌ 不支持高级模型选择

## 使用方法
1. 双击 TextTranslator_Mini.exe 启动
2. 选择翻译方向（中译英/英译中）
3. 输入文本并点击翻译

## 首次使用
首次运行时会自动下载翻译模型（约100MB），请确保网络连接。
下载完成后即可离线使用。

## 系统要求
- Windows 10/11
- 2GB+ RAM
- 500MB+ 可用磁盘空间

## 故障排除
如遇问题，请尝试：
1. 以管理员身份运行
2. 检查网络连接（首次使用）
3. 确保有足够磁盘空间
'''
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print(f"最小化便携式包已创建: {release_dir.absolute()}")
    
    total_size = sum(f.stat().st_size for f in release_dir.rglob('*') if f.is_file())
    print(f"最小化包大小: {total_size / (1024 * 1024):.1f} MB")

def main():
    """主函数"""
    print("=== 最小化翻译工具打包脚本 ===")
    print("目标：创建最小体积的文本翻译工具")
    
    try:
        # 1. 安装最小化依赖
        install_minimal_requirements()
        
        # 2. 创建最小化规格文件
        create_minimal_spec()
        
        # 3. 构建最小化可执行文件
        if build_minimal_executable():
            # 4. 创建最小化便携式包
            create_minimal_package()
            print("\n✅ 最小化打包完成！")
            print("📁 最小化可执行文件位于 release_minimal/ 目录")
            print("💡 提示：此版本仅支持文本翻译，不包含语音功能")
        else:
            print("❌ 最小化打包失败")
            
    except Exception as e:
        print(f"❌ 最小化打包过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())