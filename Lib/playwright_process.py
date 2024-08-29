from playwright.sync_api import sync_playwright
import os
import time

output_dir = './out'
os.makedirs(output_dir, exist_ok=True)

def count_words(line):
    # 统计一行中的词数，以空格分隔
    return len(line.split())

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    total_word_count = 0
    strings_array = []
    current_string = []
    
    for i, line in enumerate(lines):
        line = line.strip()  # 去掉行首尾的空白字符
        line_word_count = count_words(line)
        total_word_count += line_word_count
        
        current_string.append(line)  # 添加当前行到当前字符串中
        
        if total_word_count > 150:
            # 当前字符串超过1000词，截断并保存
            strings_array.append('\n'.join(current_string))
            # 重置统计
            total_word_count = 0
            current_string = []
    
    # 添加最后一部分（如果有剩余）
    if current_string:
        strings_array.append('\n'.join(current_string))
    
    return strings_array

def translate_text(page, text):
    # 使用CSS选择器定位输入框元素
    input_element = page.query_selector('div[contenteditable="true"][role="textbox"][aria-multiline="true"]')
    
    if input_element:
        input_element.fill('')  # 清空输入框
        input_element.fill(text)
    else:
        print("输入框元素未找到")
        return None
    
    # 使用wait_for_selector方法等待翻译结果出现
    output_element = page.wait_for_selector('section[aria-labelledby="translation-target-heading"] div[contenteditable="true"][role="textbox"][aria-multiline="true"]')
    
    if output_element:
        original_lines = len(text.split('\n')) + 1
        retry_count = 0 
        while True:
            time.sleep(1)  # 每秒检查一次
            translated_text = output_element.inner_text()
            translated_lines = len(translated_text.split('\n'))
            print(f"已翻译{translated_lines}/{original_lines}行")
            if translated_lines == original_lines or translated_lines == original_lines+1:
                return translated_text
            retry_count += 1
            if retry_count >= 10:
                print("翻译行数不匹配，刷新网页重试")
                page.reload()  # 刷新网页
                retry_count = 0  # 重置重试计数器
                
                # 重新定位输入框元素
                input_element = page.query_selector('div[contenteditable="true"][role="textbox"][aria-multiline="true"]')
                if input_element:
                    input_element.fill('')  # 清空输入框
                    input_element.fill(text)
                else:
                    print("输入框元素未找到")
                    return None
                
                # 重新定位输出框元素
                output_element = page.wait_for_selector('section[aria-labelledby="translation-target-heading"] div[contenteditable="true"][role="textbox"][aria-multiline="true"]')
                if not output_element:
                    print("翻译结果元素未找到")
                    return None
    else:
        print("翻译结果元素未找到")
        return None

def playwright_engine(source_lang, target_lang, browser_login, playwright_headless, input_file_path = 'text_extracted.txt'):
    strings_array = process_file(input_file_path)
    output_file_path = os.path.join(output_dir, 'translated_result.txt')
    with sync_playwright() as p:
        # Launch the browser
        print("正在拉起浏览器")
        browser = p.webkit.launch(executable_path="./Lib/Webkit/Playwright.exe", headless=playwright_headless)
        #browser = p.webkit.launch(headless=playwright_headless)  # Set headless=False if you want to see the browser UI
        page = browser.new_page()
        page.goto(f"https://www.deepl.com/translator#{source_lang}/{target_lang}")
        
        with open(output_file_path, 'w', encoding='utf-8') as result_file:
            for i, s in enumerate(strings_array):
                translation = translate_text(page, s)
                if translation:
                    print(f"写入翻译结果 {i + 1}, 正在尝试下一个资源段翻译")
                    result_file.write(translation)
        
        browser.close()
