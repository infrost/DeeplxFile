import subprocess
import os
import time
import requests
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from tkinter import Tk, Text, Entry, StringVar, BooleanVar, Label, OptionMenu, Button, Checkbutton, Frame, messagebox, DISABLED, NORMAL
from tkinter.ttk import Notebook, Separator
from Lib import compose, data_process, extract, direct_mode, playwright_process
from Lib.output import start_redirect, send_warning, success_message
from Lib.config import config, save_config
def run_deeplx(output_text_box):
    global processes
    exe_path = os.path.join("Lib", "deeplx_windows_amd64.exe")
    try:
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使得输出为字符串而非字节
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        processes.append(process)
        for line in process.stdout:
            print(line.strip())  # 使用 print 输出内容，这会被重定向到文本框
        # 等待进程完成
        process.wait()
        # 检查返回码
        if process.returncode != 0:
            print(f"Process finished with return code: {process.returncode}")

    except FileNotFoundError:
        print(f"The file {exe_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_process_job(source_lang, target_lang, output_text_box):
    if config.get("direct_mode", False):
        direct_mode.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
    elif config.get("playwright_mode", False):
        playwright_process.playwright_engine(
            source_lang, target_lang, config.get("force_lang_select", False), 
            config.get("browser_login", False), config.get("disable_user_profile", False),
            config.get("playwright_headless", False), config.get("playwright_path", "./Lib/Webkit/Playwright.exe"), './tmp/text_extracted.txt'
        )
    else:
        data_process.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
    
    success_message(output_text_box,f"完成翻译,正在根据原文件回写：{extract.input_path}")
    compose.compose_file(extract.file_type, extract.input_path)
    success_message(output_text_box, "翻译完成！已在输入的相同目录下生成文件")



def process_translation():
    global processes
    if config.get("direct_mode", False):
        send_warning(output_text_box,"\n【直连模式】\n当前使用直连模式请求deepl的翻译返回，不使用deeplx引擎，如果频繁请求可能会遇到错误\n该模式只能翻译较小的文件，大文件请使用deeplx引擎\n在config.json中direct_mode项设置是否直连\n")
    elif config.get("playwright_mode", False):
        print("\n启用playwright模式（测试模式）")
        if config.get("browser_login", False):
            messagebox.showinfo("警告","使用edge调用playwright会结束现有edge的所有进程\n请在执行前保存好数据！否则请取消文件导入")
        if config.get("force_lang_select", False):
            send_warning(output_text_box, "强制选择语言有时候脚本会选不上卡住，请留意提示，手动点击一下即可")
    else:
        try:
            if processes:
                print("deeplx引擎已在运行")
            else:
                print("正在启动deeplx引擎")
                deeplx_future = executor.submit(run_deeplx, output_text_box)
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

    if source_lang == "zh-Hans" or "zh-Hant":
        source_lang = "zh"
    elif source_lang == "en-US" or "en-GB":
        source_lang = "en"
    print("源语言代码:", source_lang)
    print("目标语言代码:", target_lang)
    print("等待选择文件...")

    # 解压
    extract.extract_file()
    if extract.process_cancelled:
        send_warning(output_text_box, "文件导入取消")
        extract.process_cancelled = False
        return
    success_message(output_text_box, "文档解析已完成")
    process_job = executor.submit(send_process_job, source_lang, target_lang, output_text_box)


def check_update():
    current_ver = config.get("version")
    version_url = "https://raw.githubusercontent.com/infrost/DeeplxFile/master/config.json"
    try:
        response = requests.get(version_url)
        response.raise_for_status()  # 检查请求是否成功

        data = response.json()
        online_ver = data.get("version")

        return online_ver if online_ver else None
    except requests.exceptions.RequestException as e:
        return f"网络错误: {e}"
    except ValueError as e:
        return f"数据错误: {e}"


def start_check():
    update_button.config(state=DISABLED, text = "正在检查更新...")
    update_feature = executor.submit(check_update)
    result = update_feature.result()
    if result is None:
        messagebox.showinfo("错误", "未找到可更新版本信息")
    elif "错误" in result:
        messagebox.showinfo("错误", result)
    else:
        current_ver = config.get("version")
        if result != current_ver:
            messagebox.showinfo("更新提示", 
                                f"当前版本V: {current_ver}, 有新版本可用: V{result}\n请前往下载https://github.com/infrost/DeeplxFile/releases/")
        else:
            messagebox.showinfo("更新提示", f"已是最新版本: V{current_ver}")

    update_button.config(state=NORMAL, text = "检查更新")

def save_and_exit():
    config['direct_mode'] = direct_mode_var.get()
    config['playwright_mode'] = playwright_mode_var.get()
    config['browser_login'] = browser_login_var.get()
    config['save_original'] = save_original_var.get()
    config['playwright_headless'] = playwright_headless_var.get()
    config['playwright_path'] = playwright_path_var.get() 
    config['force_lang_select'] = force_lang_select_var.get()
    config['disable_user_profile'] = disable_user_profile_var.get()
    save_config(config)
    messagebox.showinfo("成功","设置已保存")


def on_close():
    global processes
    for process in processes:
        if process:
            process.terminate()
    processes.clear()
    executor.shutdown(wait=False)
    root.destroy()  # 关闭窗口
    os._exit(0)

#这里是进程管理
processes = []
executor = ThreadPoolExecutor(max_workers=5)

#GUI
root = Tk()
root.geometry("480x500")
root.title("DeeplxFile 翻译工具")
icon_path = "./Lib/deeplxfile.ico"
root.iconbitmap(icon_path)

notebook = Notebook(root)

translate_frame = Frame(notebook)
notebook.add(translate_frame, text="翻译")


languages = [
    ("中文(简体)", "zh-Hans"),
    ("中文(繁体)","zh-Hant"),
    ("英文(美国)", "en-US"),
    ("英文(英国)", "en-GB"),
    ("日文", "ja"),
    ("韩文", "ko"),
    ("法文", "fr"),
    ("德文", "de"),
    ("俄文", "ru"),
    ("西班牙文", "es"),
    ("意大利文", "it"),
    ("葡萄牙文", "pt"),
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


# 创建输出内容流
output_text_box = Text(translate_frame, wrap='word', font=("Microsoft YaHei", 10))
output_text_box.pack(expand=True, fill='both')
output_text_box.tag_configure("default", foreground="gray")  
output_text_box.tag_configure("error", foreground="red")
output_text_box.tag_configure("warning", foreground="orange")
output_text_box.tag_configure("success", foreground="green")
io_futrue = executor.submit(start_redirect, output_text_box)


settings_frame = Frame(notebook)
notebook.add(settings_frame, text="设置")

config_label = Label(settings_frame, text="配置选项")
config_label.pack(pady=10)


direct_mode_var = BooleanVar(settings_frame)
direct_mode_var.set(config.get("direct_mode", False))
direct_mode_checkbox = Checkbutton(settings_frame, text="直连模式", variable=direct_mode_var)
direct_mode_checkbox.pack(anchor='w')

# Playwright模式
playwright_frame = Frame(settings_frame, borderwidth=2, relief="groove", pady=10)
playwright_frame.pack(padx=5, pady=5, anchor='w')  # 内边距

left_frame = Frame(playwright_frame)
left_frame.pack(side='left', padx=10)

right_frame = Frame(playwright_frame)
right_frame.pack(side='left', padx=10)

playwright_mode_var = BooleanVar(playwright_frame)
playwright_mode_var.set(config.get("playwright_mode", False))
playwright_mode_checkbox = Checkbutton(left_frame, text="Playwright模式", variable=playwright_mode_var)
playwright_mode_checkbox.pack(anchor='w')
comment_label = Label(left_frame, text="Playwright模式会模拟人类操作翻译\n会较为消耗性能，但是兼容性较强\n如果出现请求频繁错误，可以尝试该模式")
comment_label.pack(anchor='w')

browser_login_var = BooleanVar(playwright_frame)
browser_login_var.set(config.get("browser_login", False))
browser_login_checkbox = Checkbutton(left_frame, text="使用系统edge浏览器", variable=browser_login_var)
browser_login_checkbox.pack(anchor='w')
comment_label3 = Label(left_frame, text="可以提前在edge浏览器中登录账号\n 调用edge的登录状态能让\n单次翻译的字符更多，更稳定。")
comment_label3.pack(anchor='w')

disable_user_profile_var = BooleanVar(playwright_frame)
disable_user_profile_checkbox = Checkbutton(left_frame, text="edge浏览器不使用用户数据", variable=disable_user_profile_var)
disable_user_profile_checkbox.pack(anchor='w')

playwright_headless_var = BooleanVar(playwright_frame)
playwright_headless_var.set(config.get("playwright_headless", False))
playwright_headless_checkbox = Checkbutton(right_frame, text="隐藏操作过程", variable=playwright_headless_var)
playwright_headless_checkbox.pack(anchor='w')
comment_label2 = Label(right_frame, text="可以节约系统资源, 加快翻译速度")
comment_label2.pack(anchor='w', padx=5, pady=2)

force_lang_select_var = BooleanVar(playwright_frame)
force_lang_select_var.set(config.get("force_lang_select", False))
force_lang_select_checkbox = Checkbutton(right_frame, text="强制指定语言", variable=force_lang_select_var)
force_lang_select_checkbox.pack(anchor='w')
comment_label4 = Label(right_frame, text="少数情况无法正确翻译到指定语言时\n可以尝试开启，略微影响速度")
comment_label4.pack(anchor='w')

playwright_path_var = StringVar(playwright_frame)
playwright_path_var.set(config.get("playwright_path", "")) 
playwright_path_label = Label(right_frame, text="Playwright Webkit 内核路径:")
playwright_path_label.pack(anchor='w')
playwright_path_entry = Entry(right_frame, textvariable=playwright_path_var, width=30)
playwright_path_entry.pack(anchor='w', padx=5)

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

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
