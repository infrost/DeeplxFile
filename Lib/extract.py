"""
Replacing Newline Characters: Within the extract_strings_from_xlsx function, 
any newline characters within the text of each <t> tag are replaced with a space. 
This ensures that each <t> tag's content is treated as a single line when writing to the output file.

Handling Empty Tags: The code includes a check to ensure that if a <t> tag is empty (None), 
it does not cause an error.

"""

import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog

tmp_dir = './tmp'
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

input_path = ""

def extract_strings_from_xlsx(file_path):
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdirname:
        # 解压缩 .xlsx 文件
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # 读取 sharedStrings.xml 文件
        shared_strings_path = os.path.join(tmpdirname, 'xl', 'sharedStrings.xml')
        
        if not os.path.exists(shared_strings_path):
            print("sharedStrings.xml 文件不存在。")
            return []
        
        # 解析 XML 文件
        tree = ET.parse(shared_strings_path)
        root = tree.getroot()
        
        # 存储字符串
        strings = []
        
        # 查找所有 <t> 标签
        for t in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
            # 将所有换行符替换为单个空格，确保每个 <t> 标签的内容是一行
            text_content = t.text.replace('\n', ' ') if t.text else ''
            strings.append(text_content)
        
        return strings

def write_strings_to_file(strings, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for string in strings:
            f.write(f"{string}\n")


def extract_file():
    # 创建Tkinter窗口但不显示
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(title='选择一个 .xlsx 文件，目前只支持了Excel', filetypes=[('Excel files', '*.xlsx')])
    
    if not file_path:
        print("没有选择文件。")
        return
    global input_path
    input_path = file_path

    supported_files = [".xlsx",".docx"]
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in supported_files:
        print("目前只支持.xlsx文件")
        return
    if file_extension == ".xlsx":
        global file_type
        file_type = "Excel"

        strings = extract_strings_from_xlsx(file_path)

    print(f"已处理{file_type}文件: {input_path}")
    output_file = os.path.join(tmp_dir, 'text_extracted.txt')
    write_strings_to_file(strings, output_file)
    print(f"提取的字符串已写入 {output_file}")

