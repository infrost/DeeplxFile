import os
import zipfile
import xml.etree.ElementTree as ET
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
        
        # 解析 XML 文件
        tree = ET.parse(shared_strings_path)
        root = tree.getroot()
        
        # 查找所有 <t> 标签
        t_elements = list(root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'))
        
        # 确保提供的字符串数量与 <t> 标签数量匹配
        if len(strings) != len(t_elements):
            print(f"警告: 提供的字符串数量 ({len(strings)}) 与现有 <t> 标签数量 ({len(t_elements)}) 不匹配。")
        
        # 按顺序替换 <t> 标签中的文本
        for t_element, new_string in zip(t_elements, strings):
            t_element.text = new_string

        # 将修改后的 XML 写回文件
        tree.write(shared_strings_path, xml_declaration=True, encoding='UTF-8')
        
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

def compose_file(file_type, input_path):

    result_file_path = './out/translated_result.txt'
    
    # 读取文本文件内容
    result_strings = read_strings_from_file(result_file_path)

    if file_type == "Excel":
        # 更新 Excel 文件中的 sharedStrings.xml
        update_shared_strings_in_xlsx(input_path, result_strings)
        print(f"生成翻译后的电子表格...")

