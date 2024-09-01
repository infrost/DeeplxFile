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
import socket
import json
from lxml import etree as ET
from tkinter import filedialog, Tk

tmp_dir = './tmp'
input_path = ""
file_type = ""
process_cancelled = bool()
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

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


def extract_strings_from_docx(file_path):
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)

        document_path = os.path.join(tmpdirname, 'word', 'document.xml')
        
        if not os.path.exists(document_path):
            print("错误：document.xml 文件不存在，请确认是合法的word文档。")
            return []

        tree = ET.parse(document_path)
        root = tree.getroot()
        
        strings = []
        
        for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            text_content = t.text.replace('\n', ' ') if t.text else ''
            strings.append(text_content)
        
        return strings

def extract_strings_from_pptx(file_path):
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)

        slides_dir = os.path.join(tmpdirname, 'ppt', 'slides')
        
        if not os.path.exists(slides_dir):
            print("错误：slides 目录不存在，请确认是合法的 PowerPoint 文档。")
            return []

        strings = []
        
        slide_files = sorted([f for f in os.listdir(slides_dir) if f.endswith('.xml')])

        for slide_file in slide_files:
            if slide_file.endswith('.xml'):
                slide_path = os.path.join(slides_dir, slide_file)
                print(f"正在处理{slide_file}")
                tree = ET.parse(slide_path)
                root = tree.getroot()
                
                for t in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
                    text_content = t.text.replace('\n', ' ') if t.text else ''
                    strings.append(text_content)
        
        return strings

def requests_docx(message, docx_path):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 9999))

        # 发送消息到服务器
        client_socket.send(message.encode('utf-8'))
        print(f"Sent requests to server")

        # 接收服务器的响应
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Received from server..")

        # 调用docx处理流程
        strings = extract_strings_from_docx(docx_path)

    except socket.error as e:
        print(f"Socket error: {e}\n请检查PDF服务是否运行\n 如果未下载请前往下载\nhttps://github.com/infrost/pdf2docxserver/releases/")
        strings = ""
    except Exception as e:
        strings = ""
        print(f"An unexpected error occurred: {e}")
    finally:
        client_socket.close()
    return strings



def write_strings_to_file(strings, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for string in strings:
            f.write(f"{string}\n")


def extract_file():
    # 创建Tkinter窗口但不显示
    root = Tk()
    root.withdraw()  # 隐藏主窗口

    global process_cancelled
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(
        title='选择一个文件，目前支持了Excel,Word,PowerPoint', 
        filetypes=[
            ('Excel, PowerPoint, Word, PDF, Markdown, Text', '*.xlsx *.pptx *.docx *.pdf *.md *.txt'),
            ('All Files', '*.*')
            ]
        )
    
    if not file_path:
        print("没有选择文件。")
        process_cancelled = True
        return

    global input_path
    input_path = file_path

    supported_files = [".xlsx",".docx",".pptx", ".pdf", ".md", ".txt"]
    file_extension = os.path.splitext(file_path)[1].lower()
    global file_type
    if file_extension not in supported_files:
        print("错误：不受支持的文件")
        process_cancelled = True
        return
    if file_extension == ".xlsx":
        file_type = "Excel"
        strings = extract_strings_from_xlsx(file_path)
    elif file_extension == ".docx":
        file_type = "Word"
        strings = extract_strings_from_docx(file_path)
    elif file_extension == ".pptx":
        file_type = "PowerPoint"
        strings = extract_strings_from_pptx(file_path)
    elif file_extension == ".pdf":
        file_type = "PDF"
        base, _ = os.path.splitext(file_path)
        docx_path = base + '.docx'
        data = {
            "source_path": file_path,
            "output_path": docx_path,
            "arg": False
        }
        message = json.dumps(data)
        strings = requests_docx(message, docx_path)
        if not strings:
            process_cancelled = True
            return
        input_path = docx_path
    elif file_extension == ".md" or ".txt":
        if file_extension == ".md":
            file_type = "TEXT"
        else:
            file_type = "Markdown"
        
        print (f"纯文本文件，无需预处理")
        strings = []
        with open(input_path, 'r', encoding='utf-8') as file:
            for line in file:
                strings.append(line.strip())


    print(f"已处理{file_type}文件: {input_path}")
    output_file = os.path.join(tmp_dir, 'text_extracted.txt')
    write_strings_to_file(strings, output_file)
    print(f"提取的字符串已写入 {output_file}")



