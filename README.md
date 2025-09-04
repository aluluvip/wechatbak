# 微信聊天记录备份工具

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

一个简单易用的微信聊天记录文件分类提取工具，帮助您将微信桌面端的聊天记录文件按类型分类并备份到指定文件夹。

![工具截图](https://via.placeholder.com/800x600.png?text=微信聊天记录备份工具)

## 功能特点

- 图形用户界面，操作简单直观
- 自动扫描并分类微信聊天记录文件
- 支持多种文件类型分类（图片、视频、音频、文档等）
- 实时显示备份进度和日志信息
- 支持取消操作
- 自动处理重复文件
- 生成备份统计报告

## 支持的文件类型

- **图片**：.jpg, .jpeg, .png, .gif, .bmp, .webp, .heic
- **视频**：.mp4, .avi, .mov, .wmv, .flv, .mkv, .webm, .3gp
- **音频**：.mp3, .wav, .ogg, .m4a, .amr, .flac, .aac
- **文档**：.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .txt, .rtf, .csv
- **其他**：其他所有类型的文件

## 安装要求

- Python 3.6 或更高版本
- 操作系统：Windows, macOS, Linux

## 安装步骤

1. 克隆或下载此仓库

```bash
git clone https://github.com/yourusername/wechat-backup-tool.git
cd wechat-backup-tool
```

2. 安装依赖（本工具仅使用Python标准库，无需额外依赖）

## 使用方法

1. 运行程序

```bash
python wechat_backup_tool.py
```

2. 在图形界面中：
   - 点击"选择微信聊天记录文件夹"下的"浏览"按钮，选择微信聊天记录文件夹
   - 点击"选择备份目标文件夹"下的"浏览"按钮，选择备份文件存放的目标文件夹
   - 点击"开始备份"按钮，开始备份过程
   - 备份过程中可以查看进度条和日志信息
   - 如需取消备份，点击"取消"按钮

3. 备份完成后，程序会在目标文件夹中创建一个以时间命名的文件夹（格式：WeChatBackup_YYYYMMDD_HHMMSS），其中包含按文件类型分类的子文件夹。

## 微信聊天记录文件夹位置

微信聊天记录通常位于：

- **Windows**：`C:\Users\用户名\Documents\WeChat Files\wxid_xxx\FileStorage\MsgAttach`
- **Mac**：`~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/[一串数字]/Message/MessageTemp`

## 注意事项

- 备份过程中请勿关闭程序
- 如文件较多，备份可能需要一些时间
- 备份完成后会在目标文件夹中创建一个以时间命名的文件夹
- 如果目标位置已存在同名文件，程序会自动重命名文件（添加序号）

## 功能详解

### 文件扫描与分类

程序会递归扫描源文件夹中的所有文件，根据文件扩展名将其分类到不同的类别中。

### 进度显示

- 实时显示已处理文件数量和总文件数量
- 进度条直观展示备份进度
- 日志窗口显示详细操作信息

### 错误处理

- 自动跳过无法复制的文件并记录错误信息
- 完整的错误日志记录

### 备份报告

备份完成后，程序会生成一份简要的统计报告，显示各类型文件的数量。

## 开发信息

- 开发语言：Python
- GUI框架：Tkinter
- 版本：1.0.0

## 许可证

[MIT](LICENSE)

## 贡献

欢迎提交问题和改进建议！