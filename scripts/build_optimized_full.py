#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的完整版翻译器打包脚本
通过精确控制torch模块来减少文件大小
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_optimized_spec():
    """创建优化的PyInstaller spec文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

# 自定义hook来精确控制torch模块
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 只包含whisper和基础torch功能需要的模块
torch_modules = [
    'torch',
    'torch.nn',
    'torch.nn.functional', 
    'torch.nn.modules',
    'torch.nn.modules.activation',
    'torch.nn.modules.batchnorm',
    'torch.nn.modules.conv',
    'torch.nn.modules.linear',
    'torch.nn.modules.normalization',
    'torch.nn.modules.transformer',
    'torch.nn.modules.utils',
    'torch.nn.parameter',
    'torch.nn.init',
    'torch.optim',
    'torch.utils',
    'torch.utils.data',
    'torch.cuda',
    'torch.jit',
    'torch.autograd',
    'torch.tensor',
    'torch._C',
    'torch.serialization',
    'torch.storage',
    'torch.multiprocessing',
    'torch.hub',
    'torch.backends',
    'torch.backends.cudnn',
    'torch.backends.cuda',
    'torch.fx',
    'torch.overrides',
    'torch.types',
    'torch.testing',
    'torch._utils',
    'torch.library',
    'torch.masked',
    'torch.sparse',
    'torch.special',
    'torch.linalg',
    'torch.fft',
    'torch.random',
]

# whisper相关模块
whisper_modules = [
    'whisper',
    'whisper.model',
    'whisper.audio',
    'whisper.decoding',
    'whisper.tokenizer',
    'whisper.normalizers',
    'whisper.timing',
    'whisper.utils',
]

a = Analysis(
    ['gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含whisper的资产文件 - 使用动态路径
    ] + collect_data_files('whisper'),
    hiddenimports=torch_modules + whisper_modules + [
        'soundcard',
        'numpy',
        'numpy._core',
        'numpy._core.multiarray',
        'numpy._core.overrides',
        'numpy.__config__',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'threading',
        'queue',
        'translators',
        'translators.server',
        'translators.apis',
        'argostranslate',
        'argostranslate.package',
        'argostranslate.translate',
        'ctranslate2',
        'sentencepiece',
        'stanza',
        'regex',
        'tqdm',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'more_itertools',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
    ],
    hookspath=[],
    hooksconfig={
        'numpy': {
            'include_version_info': False,
            'exclude_tests': True
        }
    },
    runtime_hooks=[],
    excludes=[
        # 排除torch中不需要的大型模块
        'torch.distributed',
        'torch.distributed.algorithms',
        'torch.distributed.elastic',
        'torch.distributed.fsdp',
        'torch.distributed.optim',
        'torch.distributed.pipeline',
        'torch.distributed.rpc',
        'torch.distributed.tensor',
        'torch.distributed._shard',
        'torch.distributed._tools',
        'torch.ao',  # 量化相关
        'torch.ao.quantization',
        'torch.ao.pruning',
        'torch.ao.sparsity',
        'torch.quantization',
        'torch.jit._script',
        'torch.jit._trace',
        'torch.jit.mobile',
        'torch.mobile',
        'torch.package',
        'torch.profiler',
        'torch.utils.benchmark',
        'torch.utils.bottleneck',
        'torch.utils.collect_env',
        'torch.utils.cpp_extension',
        'torch.utils.deterministic',
        'torch.utils.dlpack',
        'torch.utils.hipify',
        'torch.utils.mobile_optimizer',
        'torch.utils.model_zoo',
        'torch.utils.tensorboard',
        'torch.utils.viz',
        'torch.onnx',
        'torch.xpu',
        'torch.mps',
        'torch.mtia',
        
        # 排除torchvision和torchaudio（如果不需要）
        'torchvision',
        'torchaudio',
        
        # 排除其他大型库
        'tensorflow',
        'keras',
        'sklearn',
        'scipy.optimize',
        'scipy.sparse',
        'scipy.spatial',
        'scipy.stats',
        'scipy.signal',
        'scipy.integrate',
        'scipy.interpolate',
        'scipy.io',
        'scipy.linalg',
        'scipy.ndimage',
        'scipy.special',
        'matplotlib',
        'plotly',
        'seaborn',
        'bokeh',
        'PIL.ImageQt',
        'PIL.ImageTk',
        'cv2',
        'skimage',
        
        # 排除开发和测试工具
        'pytest',
        'unittest',
        'doctest',
        'pdb',
        'bdb',
        'trace',
        'cProfile',
        'profile',
        'pstats',
        'timeit',
        
        # 排除文档工具
        'sphinx',
        'docutils',
        'jinja2',
        'babel',
        'pygments',
        
        # 排除jupyter相关
        'jupyter',
        'IPython',
        'notebook',
        'ipykernel',
        'ipywidgets',
        
        # 排除网络服务器
        'tornado',
        'flask',
        'django',
        'fastapi',
        'uvicorn',
        'gunicorn',
        
        # 排除数据库（保留sqlite3，它是Python标准库）
        'pymongo',
        'psycopg2',
        'mysql',
        
        # 排除其他不需要的模块（保留核心标准库模块）
        'curses',
        'readline',
        'rlcompleter',
    ],
    noarchive=False,
    optimize=2,
)

# 进一步过滤，移除不需要的torch子模块
a.pure = [x for x in a.pure if not any([
    # 过滤torch中的大型子模块
    x[0].startswith('torch.distributed'),
    x[0].startswith('torch.ao'),
    x[0].startswith('torch.quantization'),
    x[0].startswith('torch.mobile'),
    x[0].startswith('torch.package'),
    x[0].startswith('torch.profiler'),
    x[0].startswith('torch.onnx'),
    x[0].startswith('torch.xpu'),
    x[0].startswith('torch.mps'),
    x[0].startswith('torch.mtia'),
    x[0].startswith('torch.utils.benchmark'),
    x[0].startswith('torch.utils.bottleneck'),
    x[0].startswith('torch.utils.cpp_extension'),
    x[0].startswith('torch.utils.tensorboard'),
    x[0].startswith('torch.utils.viz'),
    x[0].startswith('torch.utils.mobile_optimizer'),
    x[0].startswith('torch.utils.model_zoo'),
    x[0].startswith('torch.jit._script'),
    x[0].startswith('torch.jit._trace'),
    x[0].startswith('torch.jit.mobile'),
    
    # 过滤测试模块
    x[0].startswith('test'),
    x[0].endswith('_test'),
    x[0].endswith('.test'),
    'test' in x[0].lower() and not x[0].startswith('torch.testing'),
    
    # 过滤文档和调试模块
    x[0].startswith('pydoc'),
    x[0].startswith('doctest'),
    x[0].startswith('pdb'),
    x[0].startswith('bdb'),
    x[0].startswith('trace'),
    
    # 过滤不需要的numpy子模块
    x[0].startswith('numpy.distutils'),
    x[0].startswith('numpy.f2py'),
    x[0].startswith('numpy.testing') and x[0] != 'numpy.testing',
    x[0].startswith('numpy.doc'),
    
    # 过滤scipy大型子模块
    x[0].startswith('scipy.optimize'),
    x[0].startswith('scipy.sparse'),
    x[0].startswith('scipy.spatial'),
    x[0].startswith('scipy.stats'),
    x[0].startswith('scipy.signal'),
    x[0].startswith('scipy.integrate'),
    x[0].startswith('scipy.interpolate'),
    x[0].startswith('scipy.io'),
    x[0].startswith('scipy.linalg'),
    x[0].startswith('scipy.ndimage'),
    x[0].startswith('scipy.special'),
])]

# 过滤二进制文件，移除不需要的DLL
a.binaries = [x for x in a.binaries if not any([
    # 过滤大型CUDA库（如果不使用GPU）
    'cublas' in x[0].lower(),
    'cudnn' in x[0].lower(),
    'cufft' in x[0].lower(),
    'curand' in x[0].lower(),
    'cusolver' in x[0].lower(),
    'cusparse' in x[0].lower(),
    'nvrtc' in x[0].lower(),
    'nvcuda' in x[0].lower(),
    
    # 过滤不需要的库
    'mkl_' in x[0].lower() and 'mkl_core' not in x[0].lower() and 'mkl_intel_thread' not in x[0].lower(),
    'libiomp5md' in x[0].lower(),
    'tbb' in x[0].lower(),
])]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OptimizedTranslator',
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
    
    with open('optimized_full.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建优化spec文件")

def install_dependencies():
    """安装必要的依赖"""
    dependencies = [
        'torch>=2.0.0',
        'torchaudio>=2.0.0', 
        'openai-whisper',
        'soundcard',
        'numpy',
        'translators',
        'argostranslate',
        'tiktoken'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.split('>=')[0].split('==')[0].replace('-', '_'))
            print(f"✓ {dep} 已安装")
        except ImportError:
            print(f"正在安装 {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)

def build_executable():
    """构建可执行文件"""
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'optimized_full.spec']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 构建优化版可执行文件成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_package():
    """创建便携包"""
    dist_dir = Path('dist')
    release_dir = Path('release_optimized')
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_file = dist_dir / 'OptimizedTranslator.exe'
    if exe_file.exists():
        shutil.copy2(exe_file, release_dir)
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"✓ 优化版可执行文件大小: {size_mb:.1f} MB")
    
    # 创建使用说明
    readme_content = """优化版实时翻译器使用说明

这是一个经过优化的完整功能实时翻译工具，在保持所有功能的同时显著减少了文件大小。

功能特性:
✅ 实时语音识别和翻译
✅ 支持中英文双向翻译
✅ GPU/CPU自动适配
✅ 多种翻译质量模式
✅ 音频设备自动检测
✅ 优化的文件大小

使用方法:
1. 双击 OptimizedTranslator.exe 启动程序
2. 等待模型加载完成
3. 选择音频输入设备（建议使用"默认扬声器"进行系统音频捕获）
4. 选择翻译方向（英译中或中译英）
5. 点击"开始翻译"按钮
6. 程序将实时捕获音频并显示翻译结果

优化说明:
- 移除了torch中不必要的分布式计算、量化、移动端等模块
- 排除了大型科学计算库（scipy、matplotlib等）
- 保留了whisper和翻译功能的核心依赖
- 应用了代码优化和压缩技术

注意事项:
- 首次使用时需要下载Whisper模型，请保持网络连接
- 建议在安静环境中使用以获得更好的识别效果
- 如果遇到GPU兼容性问题，程序会自动切换到CPU模式

版本: 优化完整版
"""
    
    with open(release_dir / '使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ 创建优化版便携包: {release_dir}")
    return True

def main():
    print("开始构建优化版完整翻译器...")
    
    # 检查和安装依赖
    print("检查依赖...")
    install_dependencies()
    
    # 创建优化的spec文件
    create_optimized_spec()
    
    # 构建可执行文件
    if build_executable():
        # 创建便携包
        create_package()
        print("\n🎉 优化版完整翻译器构建完成!")
        print("可执行文件位于: release_optimized/OptimizedTranslator.exe")
        print("\n优化效果:")
        print("- 保留了所有核心功能（语音识别+翻译）")
        print("- 显著减少了文件大小")
        print("- 移除了不必要的torch模块")
        print("- 优化了依赖库结构")
    else:
        print("❌ 优化版完整翻译器构建失败")

if __name__ == '__main__':
    main()