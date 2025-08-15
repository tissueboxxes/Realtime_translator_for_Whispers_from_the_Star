#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本翻译工具
支持中文转英文和英文转中文的双向翻译
使用translators库进行翻译
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False
    print("警告: argostranslate未安装，请先安装: pip install argostranslate")

class TextTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文本翻译工具 - Text Translator")
        self.root.geometry("800x600")
        
        # 翻译模式：en_to_zh (英转中) 或 zh_to_en (中转英)
        self.translation_mode = tk.StringVar(value="zh_to_en")
        
        # 初始化离线翻译
        self.translation_ready = False
        
        self.setup_ui()
        self.initialize_offline_translation()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 翻译模式选择
        mode_label = ttk.Label(main_frame, text="翻译模式:")
        mode_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        mode_combo = ttk.Combobox(main_frame, textvariable=self.translation_mode, 
                                 values=["zh_to_en", "en_to_zh"], state="readonly")
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        mode_combo.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        # 输入文本区域
        self.input_label = ttk.Label(main_frame, text="中文输入:")
        self.input_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.input_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
        self.input_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 翻译按钮
        translate_btn = ttk.Button(main_frame, text="翻译", command=self.translate_text)
        translate_btn.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # 输出文本区域
        self.output_label = ttk.Label(main_frame, text="英文翻译:")
        self.output_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 初始化界面标签
        self.update_labels()
        
    def on_mode_change(self, event=None):
        """翻译模式改变时的回调函数"""
        self.update_labels()
        # 清空文本区域
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def update_labels(self):
        """根据翻译模式更新界面标签"""
        if self.translation_mode.get() == "zh_to_en":
            self.input_label.config(text="中文输入:")
            self.output_label.config(text="英文翻译:")
        else:
            self.input_label.config(text="英文输入:")
            self.output_label.config(text="中文翻译:")
            
    def translate_text(self):
        """翻译文本"""
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("警告", "请输入要翻译的文本")
            return
            
        # 在新线程中执行翻译，避免界面卡顿
        threading.Thread(target=self._translate_worker, args=(input_text,), daemon=True).start()
        
    def initialize_offline_translation(self):
        """初始化离线翻译模型"""
        if not ARGOS_AVAILABLE:
            self.translation_ready = False
            messagebox.showerror("错误", "argostranslate未安装，请先安装: pip install argostranslate")
            return
            
        try:
            print("正在初始化离线翻译模型...")
            # 更新包索引
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # 检查并安装中英翻译包
            zh_to_en_installed = False
            en_to_zh_installed = False
            
            installed_packages = argostranslate.package.get_installed_packages()
            for package in installed_packages:
                if package.from_code == "zh" and package.to_code == "en":
                    zh_to_en_installed = True
                elif package.from_code == "en" and package.to_code == "zh":
                    en_to_zh_installed = True
            
            # 安装缺失的翻译包
            for package in available_packages:
                if package.from_code == "zh" and package.to_code == "en" and not zh_to_en_installed:
                    print("正在下载中文到英文翻译模型...")
                    argostranslate.package.install_from_path(package.download())
                    zh_to_en_installed = True
                elif package.from_code == "en" and package.to_code == "zh" and not en_to_zh_installed:
                    print("正在下载英文到中文翻译模型...")
                    argostranslate.package.install_from_path(package.download())
                    en_to_zh_installed = True
            
            self.translation_ready = zh_to_en_installed and en_to_zh_installed
            if self.translation_ready:
                print("离线翻译模型初始化完成")
            else:
                print("警告: 部分翻译模型未能安装")
                messagebox.showwarning("警告", "部分翻译模型未能安装，翻译功能可能受限")
                
        except Exception as e:
            print(f"离线翻译初始化失败: {e}")
            self.translation_ready = False
            messagebox.showerror("错误", f"离线翻译初始化失败: {e}")
    
    def _translate_worker(self, text):
        """翻译工作线程"""
        try:
            self.status_var.set("翻译中...")
            
            if not self.translation_ready:
                raise Exception("离线翻译模型未就绪，请检查argostranslate安装")
            
            # 根据翻译模式选择翻译方向
            if self.translation_mode.get() == "zh_to_en":
                # 中文转英文
                translated = argostranslate.translate.translate(text, "zh", "en")
            else:
                # 英文转中文
                translated = argostranslate.translate.translate(text, "en", "zh")
            
            # 更新输出文本区域
            self.root.after(0, self._update_output, translated)
            self.root.after(0, lambda: self.status_var.set("翻译完成"))
            
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            
    def _update_output(self, translated_text):
        """更新输出文本区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, translated_text)
        self.output_text.config(state=tk.DISABLED)
        
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    print("启动文本翻译工具...")
    app = TextTranslator()
    app.run()

if __name__ == "__main__":
    main()