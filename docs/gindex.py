#!/usr/bin/env python3
"""
自动生成Markdown目录列表的脚本（支持嵌套目录，修复链接路径）
cmd: python gindex.py #不需要指定参数和输出文件，默认为每一个当前目录下的子目录生成index.md
"""

import os
import sys
from pathlib import Path

def is_ignored_dir(dir_name):
    """判断是否为需要忽略的目录"""
    ignored_dirs = {'.git', '__pycache__', '.DS_Store'}
    return dir_name in ignored_dirs

def generate_nested_list(root_path, current_path, base_indent=0):
    """
    递归生成嵌套的目录和文件列表
    
    Args:
        root_path (str): 根目录路径（用于计算相对路径）
        current_path (str): 当前处理的目录路径
        base_indent (int): 基础缩进级别
        
    Returns:
        str: Markdown格式的嵌套列表字符串
    """
    result = ""
    # 使用4个空格作为缩进，确保符合markdown规范
    indent = "    " * base_indent
    
    # 获取当前目录下的所有项目并排序
    try:
        items = sorted(os.listdir(current_path))
    except PermissionError:
        return f"{indent}* [无法访问目录]\n"
    
    # 分离目录和文件
    directories = []
    markdown_files = []
    
    for item in items:
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path) and not is_ignored_dir(item):
            directories.append(item)
        elif os.path.isfile(item_path) and item.endswith('.md') and item != 'README.md':
            markdown_files.append(item)
    
    # 处理文件（先列出文件）
    for md_file in markdown_files:
        display_name = md_file[:-3]  # 移除 .md 扩展名
        # 计算相对于根路径的路径
        relative_dir = os.path.relpath(current_path, root_path)
        if relative_dir == '.':
            file_link = md_file
        else:
            # 规范化路径分隔符
            relative_dir = relative_dir.replace('\\', '/')
            file_link = f"{relative_dir}/{md_file}"
        result += f"{indent}* [{display_name}]({file_link})\n"
    
    # 处理目录（后列出目录）
    for directory in directories:
        dir_path = os.path.join(current_path, directory)
        
        # 添加目录项（纯文本）
        result += f"{indent}* {directory}\n"
        
        # 递归处理子目录
        sub_list = generate_nested_list(root_path, dir_path, base_indent + 1)
        if sub_list:
            result += sub_list
    
    return result

def generate_markdown_index(root_path, output_file="README.md"):
    """
    生成完整的Markdown索引文件
    
    Args:
        root_path (str): 根目录路径
        output_file (str): 输出文件名
    """
    # 规范化路径
    root_path = os.path.normpath(root_path)
    root_name = os.path.basename(root_path)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入标题
        f.write(f"# {root_name}\n\n")
        
        # 写入副标题
        f.write("## 目录\n\n")
        
        # 生成嵌套列表
        nested_list = generate_nested_list(root_path, root_path)
        if nested_list.strip():
            f.write(nested_list)
        else:
            f.write("* 暂无内容\n")


def main():
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 获取当前目录下的所有项目
    try:
        items = os.listdir(current_dir)
    except PermissionError:
        print("错误: 无法访问当前目录")
        sys.exit(1)
    
    # 筛选出所有目录（排除忽略的目录）
    directories = [item for item in items 
                  if os.path.isdir(os.path.join(current_dir, item)) 
                  and not is_ignored_dir(item)]
    
    if not directories:
        print("当前目录下没有子目录")
        return
    
    # 为每个子目录生成index.md文件
    for directory in directories:
        dir_path = os.path.join(current_dir, directory)
        output_file = os.path.join(dir_path, "README.md")
        
        try:
            generate_markdown_index(dir_path, output_file)
            print(f"已成功生成索引文件: {output_file}")
        except Exception as e:
            print(f"为目录 '{directory}' 生成索引文件时出错: {e}")

if __name__ == "__main__":
    main()