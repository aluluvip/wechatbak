#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信聊天记录文件分类提取工具

该工具用于将微信桌面端的聊天记录文件夹内的文件按文件格式分类提取到新的文件夹中，方便备份和管理。
"""

import os
import sys
import shutil
import logging
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path
import threading
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WeChatBackupTool')


class WeChatBackupTool:
    """微信聊天记录文件分类提取工具类"""
    
    def __init__(self, root):
        """初始化应用"""
        self.root = root
        self.root.title("微信聊天记录备份工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置图标和主题
        self.root.option_add('*Font', '微软雅黑 10')
        
        # 设置变量
        self.source_path = tk.StringVar()
        self.target_path = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="就绪")
        self.file_count_var = tk.StringVar(value="找到文件: 0")
        self.is_cancelled = False
        
        # 创建界面
        self._create_widgets()
        
        # 文件类型映射
        self.file_types = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic'],
            'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.3gp'],
            'audios': ['.mp3', '.wav', '.ogg', '.m4a', '.amr', '.flac', '.aac'],
            'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.csv'],
            'others': []
        }
    
    def _create_widgets(self):
        """创建GUI组件"""
        # 创建菜单栏
        self._create_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择
        source_frame = ttk.LabelFrame(main_frame, text="选择微信聊天记录文件夹", padding="10")
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(source_frame, textvariable=self.source_path, width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(source_frame, text="浏览", command=self._browse_source).pack(side=tk.RIGHT, padx=5)
        
        # 目标文件夹选择
        target_frame = ttk.LabelFrame(main_frame, text="选择备份目标文件夹", padding="10")
        target_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(target_frame, textvariable=self.target_path, width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(target_frame, text="浏览", command=self._browse_target).pack(side=tk.RIGHT, padx=5)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        start_button = ttk.Button(button_frame, text="开始备份", command=self._start_backup)
        start_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=self._cancel_backup)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        help_button = ttk.Button(button_frame, text="帮助", command=self._show_help)
        help_button.pack(side=tk.RIGHT, padx=5)
        
        # 进度显示
        progress_frame = ttk.LabelFrame(main_frame, text="备份进度", padding="10")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        status_frame = ttk.Frame(progress_frame)
        status_frame.pack(fill=tk.X)
        
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.file_count_var).pack(side=tk.RIGHT, padx=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 设置日志重定向
        self._redirect_logging()
        
        # 添加初始日志
        self.log("欢迎使用微信聊天记录备份工具！请选择微信聊天记录文件夹和备份目标文件夹，然后点击\"开始备份\"。")
        self.log("提示：微信聊天记录通常位于 C:\\Users\\用户名\\Documents\\WeChat Files\\wxid_xxx\\FileStorage\\MsgAttach")
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择源文件夹", command=self._browse_source)
        file_menu.add_command(label="选择目标文件夹", command=self._browse_target)
        file_menu.add_separator()
        file_menu.add_command(label="开始备份", command=self._start_backup)
        file_menu.add_command(label="取消", command=self._cancel_backup)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _browse_source(self):
        """浏览选择源文件夹"""
        folder = filedialog.askdirectory(title="选择微信聊天记录文件夹")
        if folder:
            self.source_path.set(folder)
            self.log(f"已选择源文件夹: {folder}")
    
    def _browse_target(self):
        """浏览选择目标文件夹"""
        folder = filedialog.askdirectory(title="选择备份目标文件夹")
        if folder:
            self.target_path.set(folder)
            self.log(f"已选择目标文件夹: {folder}")
    
    def _redirect_logging(self):
        """重定向日志到文本框"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)
        
        text_handler = TextHandler(self.log_text)
        logger.addHandler(text_handler)
    
    def log(self, message):
        """添加日志"""
        logger.info(message)
    
    def _start_backup(self):
        """开始备份操作"""
        source = self.source_path.get()
        target = self.target_path.get()
        
        if not source or not os.path.isdir(source):
            messagebox.showerror("错误", "请选择有效的微信聊天记录文件夹")
            return
        
        if not target or not os.path.isdir(target):
            messagebox.showerror("错误", "请选择有效的备份目标文件夹")
            return
        
        # 在新线程中执行备份操作
        self.backup_thread = threading.Thread(target=self._backup_process, args=(source, target))
        self.backup_thread.daemon = True
        self.backup_thread.start()
    
    def _cancel_backup(self):
        """取消备份操作"""
        self.is_cancelled = True
        self.status_var.set("已取消")
        self.log("备份操作已取消")
    
    def _backup_process(self, source_dir, target_dir):
        """执行备份过程"""
        try:
            self.status_var.set("正在扫描文件...")
            self.log(f"开始扫描源文件夹: {source_dir}")
            
            # 取消标志
            self.is_cancelled = False
            
            # 扫描所有文件
            all_files = []
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if self.is_cancelled:
                        return
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
            
            total_files = len(all_files)
            self.file_count_var.set(f"找到文件: {total_files}")
            self.log(f"共找到 {total_files} 个文件")
            
            if total_files == 0:
                self.status_var.set("未找到文件")
                messagebox.showinfo("提示", "未在选定文件夹中找到任何文件")
                return
            
            # 创建目标文件夹结构
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_root = os.path.join(target_dir, f"WeChatBackup_{backup_time}")
            os.makedirs(backup_root, exist_ok=True)
            
            # 为每种文件类型创建子文件夹
            for folder in self.file_types.keys():
                os.makedirs(os.path.join(backup_root, folder), exist_ok=True)
            
            # 分类并复制文件
            processed = 0
            self.log("开始分类并复制文件...")
            
            # 统计每种类型的文件数量
            type_counts = {t: 0 for t in self.file_types.keys()}
            
            for file_path in all_files:
                if self.is_cancelled:
                    return
                
                # 更新进度
                processed += 1
                progress = (processed / total_files) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"正在处理: {processed}/{total_files}")
                
                # 获取文件扩展名
                _, ext = os.path.splitext(file_path)
                ext = ext.lower()
                
                # 确定文件类型
                file_type = 'others'
                for type_name, extensions in self.file_types.items():
                    if ext in extensions:
                        file_type = type_name
                        break
                
                # 更新计数
                type_counts[file_type] += 1
                
                # 创建目标路径
                rel_path = os.path.relpath(file_path, source_dir)
                target_path = os.path.join(backup_root, file_type, os.path.basename(file_path))
                
                # 如果目标文件已存在，添加序号
                if os.path.exists(target_path):
                    name, ext = os.path.splitext(os.path.basename(file_path))
                    counter = 1
                    while os.path.exists(os.path.join(backup_root, file_type, f"{name}_{counter}{ext}")):
                        counter += 1
                    target_path = os.path.join(backup_root, file_type, f"{name}_{counter}{ext}")
                
                # 复制文件
                try:
                    shutil.copy2(file_path, target_path)
                    self.log(f"已复制: {os.path.basename(file_path)} -> {file_type}/")
                except Exception as e:
                    self.log(f"复制失败: {os.path.basename(file_path)} - {str(e)}")
                
                # 更新UI
                if processed % 10 == 0 or processed == total_files:
                    self.root.update_idletasks()
            
            # 完成
            self.progress_var.set(100)
            self.status_var.set("备份完成")
            
            # 显示统计信息
            stats = "\n".join([f"{t}: {c} 个文件" for t, c in type_counts.items() if c > 0])
            self.log(f"备份完成！文件统计:\n{stats}")
            
            messagebox.showinfo("完成", f"备份已完成！\n共处理 {total_files} 个文件\n\n{stats}\n\n备份文件夹: {backup_root}")
            
        except Exception as e:
            self.log(f"备份过程中发生错误: {str(e)}")
            self.status_var.set("备份失败")
            messagebox.showerror("错误", f"备份过程中发生错误:\n{str(e)}")
        
        finally:
            # 确保进度条显示正确
            if not self.is_cancelled:
                self.progress_var.set(100)


    def _show_help(self):
        """显示帮助信息"""
        help_text = """
微信聊天记录备份工具使用说明

1. 功能介绍
   本工具用于将微信桌面端的聊天记录文件夹内的文件按文件格式分类提取到新的文件夹中，方便备份和管理。

2. 使用步骤
   a. 点击"选择微信聊天记录文件夹"下的"浏览"按钮，选择微信聊天记录文件夹
   b. 点击"选择备份目标文件夹"下的"浏览"按钮，选择备份文件存放的目标文件夹
   c. 点击"开始备份"按钮，开始备份过程
   d. 备份过程中可以查看进度条和日志信息
   e. 如需取消备份，点击"取消"按钮

3. 文件分类说明
   - images: 图片文件 (.jpg, .jpeg, .png, .gif, .bmp, .webp, .heic)
   - videos: 视频文件 (.mp4, .avi, .mov, .wmv, .flv, .mkv, .webm, .3gp)
   - audios: 音频文件 (.mp3, .wav, .ogg, .m4a, .amr, .flac, .aac)
   - documents: 文档文件 (.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .txt, .rtf, .csv)
   - others: 其他类型文件

4. 微信聊天记录文件夹位置
   微信聊天记录通常位于：
   Windows: C:\\Users\\用户名\\Documents\\WeChat Files\\wxid_xxx\\FileStorage\\MsgAttach
   Mac: ~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/[一串数字]/Message/MessageTemp

5. 注意事项
   - 备份过程中请勿关闭程序
   - 如文件较多，备份可能需要一些时间
   - 备份完成后会在目标文件夹中创建一个以时间命名的文件夹
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("700x500")
        help_window.resizable(True, True)
        
        text = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(text, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
    
    def _show_about(self):
        """显示关于信息"""
        about_text = """
微信聊天记录备份工具

版本: 1.0.0

功能: 将微信桌面端的聊天记录文件夹内的文件按文件格式分类提取到新的文件夹中，方便备份和管理。

作者: AI助手

使用技术: Python, Tkinter

© 2023 保留所有权利
        """
        
        messagebox.showinfo("关于", about_text)


def main():
    """主函数"""
    root = tk.Tk()
    app = WeChatBackupTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()