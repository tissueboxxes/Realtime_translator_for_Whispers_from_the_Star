#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单翻译器打包脚本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['simple_translator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['argostranslate', 'argostranslate.package', 'argostranslate.translate'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除大型库
        'torch', 'torchvision', 'torchaudio',
        'tensorflow', 'keras',
        'numpy.random._pickle',
        'numpy.random._bounded_integers',
        'scipy', 'sklearn', 'pandas',
        'matplotlib', 'plotly', 'seaborn',
        'PIL', 'cv2', 'skimage',
        'jupyter', 'IPython', 'notebook',
        'pytest', 'unittest',
        # 网络库
        'requests', 'urllib3', 'certifi',
        # 开发工具
        'setuptools', 'pip', 'wheel',
        # 文档工具
        'sphinx', 'docutils', 'jinja2',
        # 其他
        'sqlite3', 'xml', 'html',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SimpleTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('simple.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建spec文件")

def build_executable():
    """构建可执行文件"""
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'simple.spec']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 构建可执行文件成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_package():
    """创建便携包"""
    dist_dir = Path('dist')
    release_dir = Path('release_simple')
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_file = dist_dir / 'SimpleTranslator.exe'
    if exe_file.exists():
        shutil.copy2(exe_file, release_dir)
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"✓ 可执行文件大小: {size_mb:.1f} MB")
    
    # 创建使用说明
    readme_content = """简单翻译器使用说明

这是一个轻量级的中英文翻译工具。

使用方法:
1. 双击 SimpleTranslator.exe 启动程序
2. 在输入框中输入要翻译的文本
3. 选择翻译方向（中译英或英译中）
4. 点击"翻译"按钮
5. 翻译结果将显示在下方输出框中

注意事项:
- 首次使用时需要下载翻译模型，请保持网络连接
- 程序启动后会自动检查和安装必要的翻译模型
- 如果遇到问题，请检查网络连接或重启程序

版本: 简化版
"""
    
    with open(release_dir / '使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ 创建便携包: {release_dir}")
    return True

def main():
    print("开始简单翻译器打包...")
    
    # 检查依赖
    try:
        import argostranslate
        print("✓ 检测到argostranslate")
    except ImportError:
        print("❌ 缺少argostranslate，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'argostranslate'], check=True)
    
    # 创建spec文件
    create_spec_file()
    
    # 构建可执行文件
    if build_executable():
        # 创建便携包
        create_package()
        print("\n🎉 简单翻译器打包完成!")
        print("可执行文件位于: release_simple/SimpleTranslator.exe")
    else:
        print("❌ 简单翻译器打包失败")

if __name__ == '__main__':
    main()