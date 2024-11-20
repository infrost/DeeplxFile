import os
import time
import subprocess
import psutil
from playwright.sync_api import sync_playwright
from pathlib import Path
from Lib.config import config

output_dir = './out'
os.makedirs(output_dir, exist_ok=True)
make_edge_happy = False

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

def split_text_on_line_boundary(text, midpoint):
    # 向前查找换行符
    split_point = text.rfind('\n', 0, midpoint)
    if split_point == -1:  # 如果未找到换行符
        # 向后查找换行符
        split_point = text.find('\n', midpoint)
        if split_point == -1:  # 如果仍未找到换行符
            split_point = midpoint  # 直接使用原始midpoint

    # 根据找到的分割点拆分文本，并保留换行符
    part1 = text[:split_point + 1]  # 包含换行符
    part2 = text[split_point + 1:]  # 从换行符之后开始
    return part1, part2

def initialize_edge(disable_user_profile, playwright_headless):
    # 结束现有edge进程
    print("正在尝试结束现有edge实例...")
    if os.name == 'nt':
        for proc in psutil.process_iter():
            try:
                if proc.name().lower() == "msedge.exe":
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    else:
        for proc in psutil.process_iter():
            try:
                if proc.name().lower() in ["msedge", "microsoft edge"]:
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    # 构建 Edge 默认用户数据目录路径
    print("正在构建带用户数据的调试模式edge...")
    if os.name == 'nt':  # Windows
        username = os.getlogin()
        user_data_dir = fr"C:\Users\{username}\AppData\Local\Microsoft\Edge\User Data"
        default_edge_path = Path("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
    elif os.name == 'posix':  # macOS/Linux
        username = os.path.basename(os.path.expanduser("~"))
        if 'darwin' in os.uname().sysname.lower():  # macOS
            default_edge_path = Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
            user_data_dir = f"/Users/{username}/Library/Application Support/Microsoft Edge"
        else:  # Linux
            user_data_dir = f"/home/{username}/.config/microsoft-edge"
            default_edge_path = "/usr/bin/microsoft-edge"
    else:
        raise OSError("Unsupported operating system")
    if not disable_user_profile:
        if not os.path.exists(user_data_dir):
            print(f"用户数据目录不存在: {user_data_dir}")
            user_data_dir = None
        if user_data_dir:
            #subprocess.Popen([shlex.quote(default_edge_path), '--remote-debugging-port=9222', f'--user-data-dir={user_data_dir}'])
            if playwright_headless:
                command = f'"{default_edge_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" --headless'
            else:
                command = f'"{default_edge_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}"'
            subprocess.Popen(command, shell=True)
            print("edge已启动")
        else:
            command = f'"{default_edge_path}" --remote-debugging-port=9222'
            subprocess.Popen(command, shell=True)
    else:
        if playwright_headless:
            command = f'"{default_edge_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" --inprivate --headless'
        else:
            command = f'"{default_edge_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" --inprivate'
        subprocess.Popen(command, shell = True)
        print("正在拉起不带用户数据的edge")
    return default_edge_path


def force_select(page, source_lang, target_lang):
    print("尝试强制指定源语言\n如果卡在此处可能需要手动点击一下源语言选择")
    try:
        page.wait_for_selector('span[data-testid="translator-source-lang"]')
        page.click('span[data-testid="translator-source-lang"]')

        # 使用 XPath 选择器
        lang_xpath = f'//button[@data-testid="translator-lang-option-{source_lang}"]'
        page.wait_for_selector(lang_xpath)
        page.click(lang_xpath)

        print(f"已强制指定源语言{source_lang}")
    except Exception as e:
        print(f"设置源语言时发生错误: {e}")
    print("尝试强制指定目标语言\n如果卡在此处可能需要手动点击一下目标语言选择")
    try:
        # 点击目标语言选择区域
        page.wait_for_selector('div[data-testid="translator-target-lang"]')
        page.click('div[data-testid="translator-target-lang"]')

        # 使用 XPath 选择器
        lang_xpath = f'//button[@data-testid="translator-lang-option-{target_lang}"]'
        page.wait_for_selector(lang_xpath)
        page.click(lang_xpath)

        print(f"已强制指定目标语言{target_lang}")
    except Exception as e:
        print(f"设置目标语言时发生错误: {e}")

def translate_text(page, text, source_lang, target_lang, force_lang_select):
    global make_edge_happy
    # 使用CSS选择器定位输入框元素
    input_element = page.query_selector('div[contenteditable="true"][role="textbox"][aria-multiline="true"]')
    #print(text)

    if input_element:
        input_element.fill('')  # 清空输入框
        input_element.fill(text)
    else:
        print("输入框元素未找到")
        return None
    if force_lang_select:
        force_select(page, source_lang, target_lang)

    time.sleep(1)

    # 使用wait_for_selector方法等待翻译结果出现
    output_element = page.wait_for_selector('section[aria-labelledby="translation-target-heading"] div[contenteditable="true"][role="textbox"][aria-multiline="true"]')

    if output_element:
        original_lines = len([line for line in text.split('\n') if line.strip()])
        retry_count = 0 
        while True:
            time.sleep(2)  # 每2秒检查一次
            translated_text = output_element.inner_text()
            translated_lines = [line for line in translated_text.splitlines() if line.strip()]
            #print(f"原译文{translated_text}")
            print(f"已翻译{len(translated_lines)}/{original_lines}行")
            if len(translated_lines) == original_lines:
                if not (translated_lines[-1] == '[...] 'and translated_lines[-2] == '[...] '):
                    # 创建一个新列表用于合并翻译结果和原始输入的空行
                    processed_result = []
                    translated_index = 0  # 用于跟踪翻译文本的索引
                    for line in text.split('\n'):
                        if line.strip() == "":  # 如果原始行是空行
                            processed_result.append("")  # 添加一个空行
                        else:
                            if translated_index < len(translated_lines):
                                processed_result.append(translated_lines[translated_index])  # 添加对应的翻译文本
                                translated_index += 1

                    # 将处理后的结果合并成字符串
                    translated_text = "\n".join(processed_result) + "\n"
                    return translated_text
            retry_count += 1
            if retry_count >= 4:
                # 检查是否存在字符限制提示
                char_limit_element = page.query_selector('div[data-testid="translator-character-limit-proad"]')
                if char_limit_element:
                    print("检测到字符限制，正在拆分输入文本...")
                    # 拆分文本并分别翻译
                    part1, part2 = split_text_on_line_boundary(text, len(text) // 2)
                    translated_part1 = translate_text(page, part1, source_lang, target_lang, force_lang_select)
                    translated_part2 = translate_text(page, part2, source_lang, target_lang, force_lang_select)

                    if translated_part1 is not None and translated_part2 is not None:
                        # 合并翻译结果
                        return translated_part1.strip() + "\n" + translated_part2.strip() + "\n"
                    else:
                        print("部分翻译失败，无法合并结果")
                        return None
                else:
                    print("翻译行数不匹配，刷新网页重试")
                    page.reload()  # 刷新网页
                    retry_count = 0  # 重置重试计数器

                    input_element = page.query_selector('div[contenteditable="true"][role="textbox"][aria-multiline="true"]')
                    if input_element:
                        input_element.fill('')  # 清空输入框
                        input_element.fill(text)
                    else:
                        print("输入框元素未找到")
                        return None

                    output_element = page.wait_for_selector('section[aria-labelledby="translation-target-heading"] div[contenteditable="true"][role="textbox"][aria-multiline="true"]')
                    if not output_element:
                        print("翻译结果元素未找到")
                        return None
    else:
        print("翻译结果元素未找到")
        return None

def playwright_engine(
    source_lang, target_lang, force_lang_select, 
    browser_login, disable_user_profile, 
    playwright_headless, playwright_path, input_file_path = 'text_extracted.txt', mode = 'w'
    ):
    global make_edge_happy
    if browser_login or not Path(playwright_path).exists():
        default_edge_path = initialize_edge(disable_user_profile, playwright_headless)
    strings_array = process_file(input_file_path)
    output_file_path = os.path.join(output_dir, 'translated_result.txt')
    
    with sync_playwright() as p:
        # Launch the browser
        print("正在拉起浏览器")
        if Path(playwright_path).exists() and not browser_login:
            browser = p.webkit.launch(executable_path=playwright_path, headless=playwright_headless)
            make_edge_happy = False
            page = browser.new_page()
        elif default_edge_path.exists():
            print("正在使用edge内核，但该模式可能兼容性有问题")
            browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')  # 连接到远程调试端口
            context = browser.contexts[0]  # 获取已有的上下文
            page = context.pages[0]
            make_edge_happy = True
        else:
            raise FileNotFoundError("找不到Playwright内核")
        
        page.goto(f"https://www.deepl.com/translator#{source_lang}/{target_lang}/")
        
        with open(output_file_path, mode, encoding='utf-8') as result_file:
            for i, s in enumerate(strings_array):
                translation = translate_text(page, s, source_lang, target_lang, force_lang_select)
                if translation:
                    print(f"写入翻译结果 {i + 1}, 正在尝试下一个资源段翻译")
                    result_file.write(translation)
                    result_file.flush()  # 立即写入文件
        
        browser.close()
