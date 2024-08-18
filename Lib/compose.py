import os
import zipfile
from lxml import etree as ET
import tempfile


def read_strings_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def update_shared_strings_in_xlsx(file_path, strings):
    with tempfile.TemporaryDirectory() as tmpdirname:
        # 解压缩 .xlsx 文件
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # 读取 sharedStrings.xml 文件
        shared_strings_path = os.path.join(tmpdirname, 'xl', 'sharedStrings.xml')
        
        if not os.path.exists(shared_strings_path):
            print("sharedStrings.xml 文件不存在。")
            return
        
        # 解析 XML 文件，保留原始格式
        #parser = ET.XMLParser(remove_blank_text=True, recover=True)
        tree = ET.parse(shared_strings_path)
        root = tree.getroot()
        
        # 查找所有 <t> 标签
        t_elements = list(root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'))
        
        # 确保提供的字符串数量与 <t> 标签数量匹配
        if len(strings) != len(t_elements):
            print(f"警告: 提供的字符串数量 ({len(strings)}) 与现有 <t> 标签数量 ({len(t_elements)}) 不匹配。")
        else:
            print("已匹配所有标签")
        
        # 按顺序替换 <t> 标签中的文本
        for t_element, new_string in zip(t_elements, strings):
            if config.get("save_original", False):  # 检查 config["save_original"] 的值
                t_element.text = t_element.text + new_string if t_element.text else new_string
            else:
                t_element.text = new_string

        # 将修改后的 XML 写回文件，不改变格式
        with open(shared_strings_path, 'wb') as f:
            tree.write(f, xml_declaration=True, encoding='UTF-8', pretty_print=False)

        # 将修改后的文件压缩回 .xlsx
        new_xlsx_path = file_path.replace('.xlsx', '_translated.xlsx')
        
        # 如果文件已存在，则删除
        if os.path.exists(new_xlsx_path):
            os.remove(new_xlsx_path)
        
        with zipfile.ZipFile(new_xlsx_path, 'w') as zip_ref:
            for foldername, subfolders, filenames in os.walk(tmpdirname):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, tmpdirname)
                    zip_ref.write(file_path, arcname)

def update_shared_strings_in_docx(file_path, strings):
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        shared_strings_path = os.path.join(tmpdirname, 'word', 'document.xml')
        
        if not os.path.exists(shared_strings_path):
            print("错误：document.xml 文件不存在。")
            return
        
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(shared_strings_path, parser)
        root = tree.getroot()

        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        t_elements = root.xpath('//w:t', namespaces=namespaces)
        
        if len(strings) != len(t_elements):
            print(f"警告: 提供的字符串数量 ({len(strings)}) 与现有 <t> 标签数量 ({len(t_elements)}) 不匹配。")
        
        for t_element, new_string in zip(t_elements, strings):
            if config.get("save_original", False): 
                t_element.text = (t_element.text or '') + new_string
            else:
                t_element.text = new_string

        tree.write(shared_strings_path, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        
        new_docx_path = file_path.replace('.docx', '_translated.docx')
        
        if os.path.exists(new_docx_path):
            os.remove(new_docx_path)
        
        with zipfile.ZipFile(new_docx_path, 'w') as zip_ref:
            for foldername, subfolders, filenames in os.walk(tmpdirname):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, tmpdirname)
                    zip_ref.write(file_path, arcname)

def update_shared_strings_in_pptx(file_path, strings):
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        slides_dir = os.path.join(tmpdirname, 'ppt', 'slides')
        
        if not os.path.exists(slides_dir):
            print("错误：slides 目录不存在。")
            return
        
        parser = ET.XMLParser(remove_blank_text=True)
        slide_files = sorted([f for f in os.listdir(slides_dir) if f.endswith('.xml')])

        string_index = 0

        for slide_file in slide_files:
            slide_path = os.path.join(slides_dir, slide_file)
            tree = ET.parse(slide_path, parser)
            root = tree.getroot()
            
            namespaces = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
            t_elements = root.xpath('//a:t', namespaces=namespaces)

            for t_element in t_elements:
                if string_index < len(strings):
                    t_element.text = strings[string_index]
                    string_index += 1
                else:
                    break
            
            # 更新后的内容写回幻灯片文件
            tree.write(slide_path, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        
        if string_index < len(strings):
            print(f"警告: 提供的字符串数量 ({len(strings)}) 超过了现有 <a:t> 标签数量 ({string_index})，未能完全替换。")

        new_pptx_path = file_path.replace('.pptx', '_translated.pptx')
        
        if os.path.exists(new_pptx_path):
            os.remove(new_pptx_path)
        
        with zipfile.ZipFile(new_pptx_path, 'w') as zip_ref:
            for foldername, subfolders, filenames in os.walk(tmpdirname):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, tmpdirname)
                    zip_ref.write(file_path, arcname)
        
        print(f"更新后的文件已保存为: {new_pptx_path}")

def compose_file(file_type, input_path):

    result_file_path = './out/translated_result.txt'
    
    # 读取文本文件内容
    result_strings = read_strings_from_file(result_file_path)

    if file_type == "Excel":
        # 更新 Excel 文件中的 sharedStrings.xml
        update_shared_strings_in_xlsx(input_path, result_strings)
        print(f"生成翻译后的电子表格...")

    if file_type == "Word":
        update_shared_strings_in_docx(input_path, result_strings)
        print(f"生成翻译后的word文档...")

    if file_type == "PowerPoint":
        update_shared_strings_in_pptx(input_path, result_strings)
        print(f"生成翻译后的ppt文档...")

def dev_mode():
    file_type = "PowerPoint"
    input_path = r"C:\Users\skyts\Desktop\开会班组员工.pptx"
    compose_file (file_type, input_path)



