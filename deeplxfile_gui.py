import threading
import subprocess
import os
import time
import requests
import json
import sys
from tkinter import Tk, Entry, StringVar, BooleanVar, Label, OptionMenu, Button, Checkbutton, Frame, messagebox, DISABLED, NORMAL
from tkinter.ttk import Notebook, Separator
from Lib import compose, data_process, extract, direct_mode, playwright_process
from Lib.config import config, save_config


def run_deeplx():
    exe_path = os.path.join("Lib", "deeplx_windows_amd64.exe")
    
    try:
        # 使用 subprocess 调用可执行文件
        subprocess.run([exe_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running deeplx_windows_amd64.exe: {e}")
    except FileNotFoundError:
        print(f"The file {exe_path} was not found.")


def process_translation():
    if config.get("direct_mode", False):
        print("\n【直连模式】\n当前使用直连模式请求deepl的翻译返回，不使用deeplx引擎，如果频繁请求可能会遇到错误\n该模式只能翻译较小的文件，大文件请使用deeplx引擎\n在config.json中direct_mode项设置是否直连\n")
    elif config.get("playwright_mode", False):
        print("\n启用playwright模式（测试模式）")
    else:
        try:
            deeplx_thread = threading.Thread(target=run_deeplx)
            deeplx_thread.start()
            print("正在启动deeplx引擎")
        except Exception as e:
            print(f"Deeplx引擎异常，尝试使用直连模式 {e}")
            config['direct_mode'] = True
            save_config(config)
            print("已将direct_mode设置为True")
    source_lang_name = source_lang_var.get()
    target_lang_name = target_lang_var.get()

    # 遍历 languages 列表，找到对应的语言代码
    source_lang = next(lang[1] for lang in languages if lang[0] == source_lang_name)
    target_lang = next(lang[1] for lang in languages if lang[0] == target_lang_name)

    print("源语言代码:", source_lang)
    print("目标语言代码:", target_lang)
    print("等待选择文件...")

    # 解压
    extract.extract_file()
    if extract.process_cancelled:
        print("文件导入取消")
        extract.process_cancelled = False
        return
    print("完成解压")

    if config.get("direct_mode", False):
        direct_mode.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
    elif config.get("playwright_mode", False):
        playwright_process.playwright_engine(source_lang, target_lang, config.get("browser_login", False), config.get("playwright_headless", False), config.get("playwright_path", "./Lib/Webkit/Playwright.exe"), './tmp/text_extracted.txt')
    else:
        data_process.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
        print(f"完成翻译,正在回写{extract.input_path}")

    # 生成翻译文件
    compose.compose_file(extract.file_type, extract.input_path)

    print("更新完成！已在输入的相同目录下生成文件")
    messagebox.showinfo("完成", "翻译完成！")

def check_update():
    update_button.config(state=DISABLED, text = "正在检查更新...")
    current_ver = config.get("version")
    version_url = "https://raw.githubusercontent.com/infrost/DeeplxFile/master/config.json"
    try:
        response = requests.get(version_url)
        response.raise_for_status()  # 检查请求是否成功

        data = response.json()
        online_ver = data.get("version")

        if online_ver:
            if online_ver != current_ver:
                messagebox.showinfo("更新提示", f"DeeplxFile当前版本V: {current_ver}, 有新版本可用: V{online_ver}\n请前往下载https://github.com/infrost/DeeplxFile/releases/")
            else:
                messagebox.showinfo("更新提示", f"DeeplxFile已是最新版本: V{current_ver}")
        else:
            print("未找到可更新版本信息")
    except requests.exceptions.RequestException as e:
        print(f"版本更新检查出错 ，请检查网络{e}")
    except ValueError as e:
        print(f"版本检查：未知错误 {e}")
    update_button.config(state=NORMAL, text = "检查更新")

def start_check():
    check_update_thread = threading.Thread(target=check_update)
    check_update_thread.start()

def save_and_exit():
    config['direct_mode'] = direct_mode_var.get()
    config['playwright_mode'] = playwright_mode_var.get()
    config['browser_login'] = browser_login_var.get()
    config['save_original'] = save_original_var.get()
    config['playwright_headless'] = playwright_headless_var.get()
    config['playwright_path'] = playwright_path_var.get() 
    save_config(config)
    messagebox.showinfo("成功","设置已保存")

#GUI
root = Tk()
#root.geometry("200x330")
root.title("DeeplxFile 翻译工具")


notebook = Notebook(root)

translate_frame = Frame(notebook)
notebook.add(translate_frame, text="翻译")


languages = [
    ("中文", "ZH"),
    ("英文", "EN"),
    ("日文", "JA"),
    ("韩文", "KO"),
    ("法文", "FR"),
    ("德文", "DE"),
    ("俄文", "RU"),
    ("西班牙文", "ES"),
    ("意大利文", "IT"),
    ("葡萄牙文", "PT"),
]

source_lang_var = StringVar(translate_frame)
target_lang_var = StringVar(translate_frame)
source_lang_var.set(languages[0][0])
target_lang_var.set(languages[1][0])

source_label = Label(translate_frame, text="选择源语言:")
source_label.pack(pady=(10, 5))

source_menu = OptionMenu(translate_frame, source_lang_var, *[lang[0] for lang in languages])
source_menu.pack(pady=10)

target_label = Label(translate_frame, text="选择目标语言:")
target_label.pack(pady=(10, 5))

target_menu = OptionMenu(translate_frame, target_lang_var, *[lang[0] for lang in languages])
target_menu.pack()

Separator(translate_frame, orient='horizontal').pack(fill='x', pady=10)

start_button = Button(translate_frame, text="选择文件", command=process_translation)
start_button.pack(pady=20)


settings_frame = Frame(notebook)
notebook.add(settings_frame, text="设置")

config_label = Label(settings_frame, text="配置选项:")
config_label.pack(pady=10)


direct_mode_var = BooleanVar(settings_frame)
direct_mode_var.set(config.get("direct_mode", False))
direct_mode_checkbox = Checkbutton(settings_frame, text="直连模式", variable=direct_mode_var)
direct_mode_checkbox.pack(anchor='w')

# Playwright模式
playwright_frame = Frame(settings_frame, borderwidth=2, relief="groove", pady=10)
playwright_frame.pack(padx=5, pady=5,anchor='w')  # 内边距

playwright_mode_var = BooleanVar(playwright_frame)
playwright_mode_var.set(config.get("playwright_mode", False))


playwright_mode_checkbox = Checkbutton(playwright_frame, text="Playwright模式", variable=playwright_mode_var)
playwright_mode_checkbox.pack(anchor='w')

comment_label = Label(playwright_frame, text="Playwright模式会模拟人类操作翻译\n会较为消耗性能，但是兼容性较强\n如果出现请求频繁错误，可以尝试该模式")
comment_label.pack(anchor='w')

browser_login_var = BooleanVar(playwright_frame)
browser_login_var.set(config.get("browser_login", False))
browser_login_checkbox = Checkbutton(playwright_frame, text="手动登入账号", variable=browser_login_var)
browser_login_checkbox.pack(anchor='w', pady = 10)

playwright_headless_var = BooleanVar(playwright_frame)
playwright_headless_var.set(config.get("playwright_headless", False))
playwright_headless_checkbox = Checkbutton(playwright_frame, text="隐藏操作过程", variable=playwright_headless_var)
playwright_headless_checkbox.pack(anchor='w')

comment_label2 = Label(playwright_frame, text="隐藏后可以节约系统资源，加快翻译速度")
comment_label2.pack(anchor='w')

playwright_path_var = StringVar(playwright_frame)
playwright_path_var.set(config.get("playwright_path", "")) 
playwright_path_label = Label(playwright_frame, text="Playwright 内核路径:")
playwright_path_label.pack(anchor='w')
playwright_path_entry = Entry(playwright_frame, textvariable=playwright_path_var, width=30)
playwright_path_entry.pack(anchor='w',padx = 5)



save_original_var = BooleanVar(settings_frame)
save_original_var.set(config.get("save_original", False))
save_original_checkbox = Checkbutton(settings_frame, text="保留原文", variable = save_original_var)
save_original_checkbox.pack(anchor='w')

Separator(settings_frame, orient='horizontal').pack(fill='x', pady=20)


save_button = Button(settings_frame, text="保存设置", command=save_and_exit)
save_button.pack(pady=(0, 10))

update_button = Button(settings_frame, text="检查更新", command=start_check)
update_button.pack()

about_label = Label(settings_frame, text= f"DeeplxFile by Kevin V{config.get("version")}")
about_label.pack(pady=10)

notebook.pack(expand=True, fill="both")

root.mainloop()
