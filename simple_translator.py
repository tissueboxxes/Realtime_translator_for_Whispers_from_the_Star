#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超简单文本翻译器 - 最小化版本
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os

# 全局变量
translator = None
models_installed = False

def lazy_import():
    """延迟导入翻译库"""
    global translator
    try:
        import argostranslate.package
        import argostranslate.translate
        translator = argostranslate.translate
        return True
    except ImportError:
        return False

def install_models():
    """安装翻译模型"""
    global models_installed
    try:
        import argostranslate.package
        
        # 更新包索引
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # 安装中英翻译包
        packages_to_install = []
        for package in available_packages:
            if (package.from_code == 'zh' and package.to_code == 'en') or \
               (package.from_code == 'en' and package.to_code == 'zh'):
                packages_to_install.append(package)
        
        for package in packages_to_install:
            argostranslate.package.install_from_path(package.download())
        
        models_installed = True
        return True
    except Exception as e:
        print(f"模型安装失败: {e}")
        return False

class SimpleTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("简单翻译器")
        self.root.geometry("600x500")
        
        self.setup_ui()
        self.check_models()
    
    def setup_ui(self):
        # 输入区域
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(input_frame, text="输入文本:").pack(anchor=tk.W)
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制区域
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 翻译方向
        ttk.Label(control_frame, text="翻译方向:").pack(side=tk.LEFT)
        self.direction_var = tk.StringVar(value="zh-en")
        direction_combo = ttk.Combobox(control_frame, textvariable=self.direction_var, 
                                     values=["zh-en", "en-zh"], state="readonly", width=10)
        direction_combo.pack(side=tk.LEFT, padx=5)
        
        # 翻译按钮
        translate_btn = ttk.Button(control_frame, text="翻译", command=self.translate)
        translate_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="正在检查模型...")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)
        
        # 输出区域
        output_frame = ttk.Frame(self.root)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(output_frame, text="翻译结果:").pack(anchor=tk.W)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def check_models(self):
        """检查模型"""
        def check():
            if lazy_import():
                if install_models():
                    self.status_var.set("就绪")
                else:
                    self.status_var.set("模型安装失败")
            else:
                self.status_var.set("缺少翻译库")
        
        threading.Thread(target=check, daemon=True).start()
    
    def translate(self):
        """翻译文本"""
        if not models_installed:
            messagebox.showwarning("警告", "翻译模型尚未就绪")
            return
        
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            return
        
        def do_translate():
            try:
                direction = self.direction_var.get()
                from_code = direction.split('-')[0]
                to_code = direction.split('-')[1]
                
                result = translator.translate(text, from_code, to_code)
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert("1.0", result)
            except Exception as e:
                messagebox.showerror("错误", f"翻译失败: {str(e)}")
        
        threading.Thread(target=do_translate, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

def main():
    app = SimpleTranslator()
    app.run()

if __name__ == "__main__":
    main()