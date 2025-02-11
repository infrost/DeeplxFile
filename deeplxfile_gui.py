import subprocess
import os
import time
import requests
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from tkinter import Tk, Text, Entry, StringVar, BooleanVar, Label, OptionMenu, Button, Checkbutton, Frame, messagebox, DISABLED, NORMAL, Radiobutton
from tkinter.ttk import Notebook, Separator, Style
from Lib import compose, data_process, extract, direct_mode, playwright_process, continue_trans, llm_translate
from Lib.output import start_redirect, send_warning, success_message
from Lib.config import config, save_config

def run_deeplx(output_text_box):
    global processes
    exe_path = os.path.join("Lib", 
                        "deeplx_windows_amd64" if os.name == 'nt' 
                        else "deeplx_darwin_amd64" if os.name == 'posix' 
                        else "deeplx_linux_amd64")
    try:
        process_args = [exe_path]
        if os.name == 'nt':
            process = subprocess.Popen(
                process_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW # Windows特有的创建参数
            )
        else:
            # 非Windows系统
            process = subprocess.Popen(
                process_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
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
    if config.get("translation_mode") == "direct":
        direct_mode.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
    elif config.get("translation_mode") == "playwright":
        playwright_process.playwright_engine(
            source_lang, target_lang, config.get("force_lang_select", False), 
            config.get("browser_login", False), config.get("disable_user_profile", False),
            config.get("playwright_headless", False), config.get("playwright_path", "./Lib/Webkit/Playwright.exe"), './tmp/text_extracted.txt'
        )
    elif config.get("translation_mode") == "llm":
        print("正在请求大模型翻译")
        llm_translate.llm_process('./tmp/text_extracted.txt', source_lang, target_lang, config.get("llm_api_base", "https://api.openai.com/v1"), config.get("llm_api_key", ""), config.get("llm_model", "gpt-4-turbo"), config.get("llm_max_token", 4096), config.get("llm_prompt", ""), mode = 'w', retries = 3, delay = 5)
    else:
        data_process.process_file('./tmp/text_extracted.txt', source_lang, target_lang, config.get("deepl_token", ""))
    
    success_message(output_text_box,f"完成翻译,正在根据原文件回写：{extract.input_path}")
    compose.compose_file(extract.file_type, extract.input_path, config.get("enhance_mode", False))
    success_message(output_text_box, "翻译完成！已在输入的相同目录下生成文件")



def process_translation():
    global processes
    if config.get("translation_mode") == "direct":
        send_warning(output_text_box,"\n【直连模式】\n当前使用直连模式请求deepl的翻译返回，不使用deeplx引擎，如果频繁请求可能会遇到错误\n该模式只能翻译较小的文件，大文件请使用deeplx引擎")
    elif config.get("translation_mode") == "playwright":
        print("\n启用playwright模式（测试模式）")
        if config.get("browser_login", False):
            messagebox.showinfo("警告","使用edge调用playwright会结束现有edge的所有进程\n请在执行前保存好数据！否则请取消文件导入")
        if config.get("force_lang_select", False):
            send_warning(output_text_box, "强制选择语言有时候脚本会选不上卡住，请留意提示，手动点击一下即可")
    elif config.get("translation_mode") == "llm":
        print("\n启用大模型模式（测试模式）")
        if config.get("llm_prompt") and config.get("llm_prompt") is not None:
            send_warning(output_text_box, f"自定义翻译要求:{config.get('llm_prompt')}")
    else:
        try:
            if processes:
                print("deeplx引擎已在运行")
            else:
                if config.get("deeplx_server",False):
                    print("使用自定的deeplx引擎")
                else:
                    print("正在启动deeplx引擎")
                    deeplx_future = executor.submit(run_deeplx, output_text_box)
        except Exception as e:
            print(f"Deeplx引擎异常，尝试使用直连模式 {e}")
            config['translation_mode'] = "direct"
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
    extract.extract_file(config.get("enhance_mode", False))
    if extract.process_cancelled:
        send_warning(output_text_box, "文件导入取消")
        extract.process_cancelled = False
        return
    success_message(output_text_box, "文档解析已完成")
    process_job = executor.submit(send_process_job, source_lang, target_lang, output_text_box)

def recover_mode():
    messagebox.showinfo("提示", "请选择上次需要翻译的原始文档")
    extract.extract_file(config.get("enhance_mode", False))
    if extract.process_cancelled:
        send_warning(output_text_box, "文件导入取消")
        extract.process_cancelled = False
        return
    success_message(output_text_box, "文档解析已完成")
    compose.compose_file(extract.file_type, extract.input_path, config.get("enhance_mode", False))
    success_message(output_text_box, "已尝试将已翻译内容恢复至输入目录同名_translated文件")
    messagebox.showinfo("成功", "文档已恢复至输入目录同名_translated文件")

def continue_translation():
    source_lang_name = source_lang_var.get()
    target_lang_name = target_lang_var.get()
    source_lang = next(lang[1] for lang in languages if lang[0] == source_lang_name)
    target_lang = next(lang[1] for lang in languages if lang[0] == target_lang_name)
    if source_lang == "zh-Hans" or "zh-Hant":
        source_lang = "zh"
    elif source_lang == "en-US" or "en-GB":
        source_lang = "en"
    print("源语言代码:", source_lang)
    print("目标语言代码:", target_lang)
    messagebox.showinfo("提示", "请选择上次需要翻译的原始文档")
    extract.extract_file(config.get("enhance_mode", False))
    if extract.process_cancelled:
        send_warning(output_text_box, "文件导入取消")
        extract.process_cancelled = False
        return
    success_message(output_text_box, "文档解析已完成")
    print("读取上次翻译进度")
    continue_trans.move_lines()
    process_job = executor.submit(send_continue_job, source_lang, target_lang, output_text_box)
    messagebox.showinfo("提示", "翻译任务已提交，请留意`翻译`页控制台提示")
    
def send_continue_job(source_lang, target_lang, output_text_box):
    send_warning(output_text_box, "以继续模式翻译时，请确保与上次翻译的文档是相同的")
    global processes
    if config.get("translation_mode") == "direct":
        direct_mode.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
    elif config.get("translation_mode") == "playwright":
        if config.get("browser_login", False):
            messagebox.showinfo("警告","使用edge调用playwright会结束现有edge的所有进程\n请在执行前保存好数据！否则请取消文件导入")
        if config.get("force_lang_select", False):
            send_warning(output_text_box, "强制选择语言有时候脚本会选不上卡住，请留意提示，手动点击一下即可")
        print("starting playwright engine...")
        playwright_process.playwright_engine(
            source_lang, target_lang, config.get("force_lang_select", False), 
            config.get("browser_login", False), config.get("disable_user_profile", False),
            config.get("playwright_headless", False), config.get("playwright_path", "./Lib/Webkit/Playwright.exe"),
            './tmp/text_extracted.txt', mode = 'a'
        )
    else:
        try:
            if processes:
                print("deeplx引擎已在运行")
            else:
                if config.get("deeplx_server",False):
                    print("使用自定的deeplx引擎")
                else:
                    print("正在启动deeplx引擎")
                    deeplx_future = executor.submit(run_deeplx, output_text_box)
        except Exception as e:
            print(f"Deeplx引擎异常，尝试使用直连模式 {e}")
            config['translation_mode'] = "direct"
            save_config(config)
            print("已将direct_mode设置为True")
        data_process.process_file('./tmp/text_extracted.txt', source_lang, target_lang, config.get("deepl_token", ""))
    success_message(output_text_box,f"完成翻译,正在根据原文件回写：{extract.input_path}")
    #continue_trans.prepend_to_translated_result()
    compose.compose_file(extract.file_type, extract.input_path, config.get("enhance_mode", False))
    success_message(output_text_box, "翻译完成！已在输入的相同目录下生成文件")


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
    global warn_label
    global playwright_label
    #config['direct_mode'] = direct_mode_var.get()
    #config['playwright_mode'] = playwright_mode_var.get()
    config['browser_login'] = browser_login_var.get()
    config['save_original'] = save_original_var.get()
    config['playwright_headless'] = playwright_headless_var.get()
    config['playwright_path'] = playwright_path_var.get() 
    config['force_lang_select'] = force_lang_select_var.get()
    config['disable_user_profile'] = disable_user_profile_var.get()
    config['translation_mode'] = translation_mode_var.get()
    config['enhance_mode'] = enhance_mode_var.get()
    config['deepl_token'] = deepl_token_var.get()
    config['deeplx_server'] = deeplx_server_var.get()
    config['llm_api_base'] = llm_api_base_var.get()
    config['llm_api_key'] = llm_api_key_var.get()
    config['llm_model'] = llm_model_var.get()
    config['llm_max_token'] = llm_max_token_var.get()
    config['llm_prompt'] = llm_prompt_var.get()
    save_config(config)
    if config.get("translation_mode") == "playwright":
        if "playwright_label" in globals() and playwright_label is not None:
            playwright_label.destroy()  # 移除旧的Label
        playwright_label = None
    elif not "playwright_label" in globals() or playwright_label is None:
        playwright_label = Label(settings_frame, text="若要使用本页设置中的功能，请在翻译设置中选择`playwright模式`", fg="red")
        playwright_label.pack(pady=10)


    if config.get("translation_mode") == "llm":
        if "warn_label" in globals() and warn_label is not None:
            warn_label.destroy()  # 移除旧的Label
        warn_label = None
    elif not "warn_label" in globals() or warn_label is None:
        warn_label = Label(llm_frame, text="若要使用本页设置中的功能，请在翻译设置中选择`大模型`", fg="red")
        warn_label.pack(pady=10)

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


"""

这里开始为GUI窗口绘制

"""
#GUI
root = Tk()
root.title("DeeplxFile 翻译工具")
if os.name == 'nt':
    icon_path = "./Lib/deeplxfile.ico" 
    root.geometry("500x520") 
else:
    icon_path = "./Lib/deeplxfile.icns"
    root.geometry("570x550")
root.iconbitmap(icon_path)
#i18n.change_locale('en')
default_font = ("Microsoft YaHei", 10)  # 设定字体为Arial，大小为12
root.option_add("*Font", default_font)

notebook = Notebook(root)


"""

翻译选项卡

"""
translate_frame = Frame(notebook)
notebook.add(translate_frame, text="翻译")
style = Style()
style.configure("TNotebook.Tab", font=("Microsoft YaHei", 12))  # 设置 notebook 选项卡字体大小

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

#Separator(translate_frame, orient='horizontal').pack(fill='x', pady=10)

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


"""

翻译设置

"""

trans_config_frame = Frame(notebook)
notebook.add(trans_config_frame, text="翻译设置")

radio_frame = Frame(trans_config_frame, bd=2, relief="groove")
radio_frame.pack(pady=10, padx=10, fill="x")
mode_config_label = Label(radio_frame, text="翻译模式")
mode_config_label.pack()
translation_mode_var = StringVar(radio_frame)
translation_mode_var.set(config.get("translation_mode", "")) 
Radiobutton(radio_frame, text="直连模式", variable=translation_mode_var, value="direct").pack(anchor='w')
Radiobutton(radio_frame, text="大模型 (测试阶段，支持翻译要求)", variable=translation_mode_var, value="llm").pack(anchor='w')
Radiobutton(radio_frame, text="Playwright (兼容性好，默认)", variable=translation_mode_var, value="playwright").pack(anchor='w')
Radiobutton(radio_frame, text="Deeplx (速度快，小文件可用)", variable=translation_mode_var, value="deeplx").pack(anchor='w')
deepl_token_var = StringVar(radio_frame)
deepl_token_var.set(config.get("deepl_token", "")) 
deepl_token_var_label = Label(radio_frame, text="Deepl Pro 密钥: (留空采用免费方法)")
deepl_token_var_label.pack(anchor='w', padx=25)
deepl_token_var_entry = Entry(radio_frame, textvariable=deepl_token_var, width=30)
deepl_token_var_entry.pack(anchor='w', padx=25, pady=5)

deeplx_server_var = StringVar(radio_frame)
deeplx_server_var.set(config.get("deeplx_server", "")) 
deeplx_server_var_label = Label(radio_frame, text="Deeplx服务器地址: (e.g.127.0.0.1:1188, 留空使用自带的)")
deeplx_server_var_label.pack(anchor='w', padx=25)
deeplx_server_var_entry = Entry(radio_frame, textvariable=deeplx_server_var, width=30)
deeplx_server_var_entry.pack(anchor='w', padx=25, pady=5)


doc_config_frame = Frame(trans_config_frame, bd=2, relief="groove")
doc_config_frame.pack(pady=10, padx=10, fill="x")
doc_config_label = Label(doc_config_frame, text="文档处理")
doc_config_label.pack()

save_original_var = BooleanVar(doc_config_frame)
save_original_var.set(config.get("save_original", False))
save_original_checkbox = Checkbutton(doc_config_frame, text="保留原文", variable = save_original_var)
save_original_checkbox.pack(anchor='w')

enhance_mode_var = BooleanVar(doc_config_frame)
enhance_mode_var.set(config.get("enhance_mode", False))
enhance_mode_checkbox = Checkbutton(doc_config_frame, text="增强模式(beta)", variable = enhance_mode_var)
enhance_mode_checkbox.pack(anchor='w')
enhance_mode_label = Label(doc_config_frame, text="增强模式会尝试翻译文档中SmartArt，Excel中工作表Sheet的表名等内容")
enhance_mode_label.pack(anchor='w', padx = 15)

save_button = Button(trans_config_frame, text="保存设置", command=save_and_exit)
save_button.pack(pady=(0, 10))


"""

Playwright设置

"""

settings_frame = Frame(notebook)
notebook.add(settings_frame, text="playwright设置")

# Playwright模式
comment_label = Label(settings_frame, text="Playwright模式会模拟人类操作翻译\n会较为消耗性能，但是兼容性较强\n如果出现请求频繁错误，可以尝试该模式\n\n若使用Edge，可以提前在edge浏览器中登录账号\n 调用edge的登录状态能让单次翻译的字符更多，更稳定。")
comment_label.pack(pady=10)

playwright_frame = Frame(settings_frame, borderwidth=2, relief="groove", pady=10)
playwright_frame.pack(padx=5, pady=5, anchor='w')  # 内边距
left_frame = Frame(playwright_frame)
left_frame.pack(side='left', padx=10)

browser_login_var = BooleanVar(playwright_frame)
browser_login_var.set(config.get("browser_login", False))
browser_login_checkbox = Checkbutton(left_frame, text="使用系统edge浏览器", variable=browser_login_var)
browser_login_checkbox.pack(anchor='w')
#comment_label3 = Label(left_frame, text="可以提前在edge浏览器中登录账号\n 调用edge的登录状态能让\n单次翻译的字符更多，更稳定。")
#comment_label3.pack(anchor='w')

disable_user_profile_var = BooleanVar(playwright_frame)
disable_user_profile_checkbox = Checkbutton(left_frame, text="edge浏览器不使用用户数据", variable=disable_user_profile_var)
disable_user_profile_checkbox.pack(anchor='w')

playwright_headless_var = BooleanVar(playwright_frame)
playwright_headless_var.set(config.get("playwright_headless", False))
playwright_headless_checkbox = Checkbutton(left_frame, text="隐藏操作过程", variable=playwright_headless_var)
playwright_headless_checkbox.pack(anchor='w')
comment_label2 = Label(left_frame, text="可以节约系统资源, 加快翻译速度")
comment_label2.pack(anchor='w', padx=5, pady=2)

right_frame = Frame(playwright_frame)
right_frame.pack(side='left', padx=10)

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

#Separator(settings_frame, orient='horizontal').pack(fill='x', pady=20)


save_button = Button(settings_frame, text="保存设置", command=save_and_exit)
save_button.pack(pady=(0, 10))

if config.get("translation_mode") != "playwright":
    playwright_label = Label(settings_frame, text="若要使用本页设置中的功能，请在翻译设置中选择`playwright模式`", fg="red")
    playwright_label.pack(pady=10)


"""

大模型翻译

"""

llm_frame = Frame(notebook)
notebook.add(llm_frame, text="大模型翻译(测试)")

llm_api_base_var = StringVar(llm_frame)
llm_api_base_var.set(config.get("llm_api_base", "")) 
llm_api_base_var_label = Label(llm_frame, text="\n大模型API地址:")
llm_api_base_var_label.pack(anchor='w')
llm_api_base_var_entry = Entry(llm_frame, textvariable=llm_api_base_var, width=35)
llm_api_base_var_entry.pack(anchor='w', padx=5)

llm_api_key_var = StringVar(llm_frame)
llm_api_key_var.set(config.get("llm_api_key", ""))
llm_api_key_var_label = Label(llm_frame, text="\n大模型API密钥:")
llm_api_key_var_label.pack(anchor='w')
llm_api_key_var_entry = Entry(llm_frame, textvariable=llm_api_key_var, width=35)
llm_api_key_var_entry.pack(anchor='w', padx=5)

llm_model_var = StringVar(llm_frame)
llm_model_var.set(config.get("llm_model", ""))
llm_model_var_label = Label(llm_frame, text="\n大模型名称:")
llm_model_var_label.pack(anchor='w')
llm_model_var_entry = Entry(llm_frame, textvariable=llm_model_var, width=35)
llm_model_var_entry.pack(anchor='w', padx=5)

llm_max_token_var = StringVar(llm_frame)
llm_max_token_var.set(config.get("llm_max_token", ""))
llm_max_token_var_label = Label(llm_frame, text="\n单次翻译长度限制（4096大约消耗1500token）:")
llm_max_token_var_label.pack(anchor='w')
llm_max_token_var_entry = Entry(llm_frame, textvariable=llm_max_token_var, width=35)
llm_max_token_var_entry.pack(anchor='w', padx=5)

llm_prompt_var = StringVar(llm_frame)
llm_prompt_var.set(config.get("llm_prompt", ""))
llm_prompt_var_label = Label(llm_frame, text="自定义翻译要求\n(如：“这是一封商务信函，请使用庄严体翻译”等，可留空):")
llm_prompt_var_label.pack(anchor='w')
llm_prompt_var_entry = Entry(llm_frame, textvariable=llm_prompt_var, width=50)
llm_prompt_var_entry.pack(anchor='w', padx=5)

save_button = Button(llm_frame, text="保存设置", command=save_and_exit)
save_button.pack(pady=(0, 10))

info_label = Label(llm_frame, text="大模型翻译是测试功能，可能会有不稳定的情况\n目前只支持openai/openai like的API\n大模型速度取决于所选模型，请耐心等待", fg="blue")
info_label.pack(pady=10)

if config.get("translation_mode") != "llm":
    warn_label = Label(llm_frame, text="若要使用本页设置中的功能，请在翻译设置中选择`大模型`", fg="red")
    warn_label.pack(pady=10)

"""

About

"""

about_frame = Frame(notebook)
notebook.add(about_frame, text="其他")


recovery_button = Button(about_frame, text="文档恢复", command=recover_mode)
recovery_button.pack(padx=10, pady =10)
recover_mode_label = Label(about_frame, text="若上一次翻译因错误或意外退出，可尝试保存上一次已翻译的部分")
recover_mode_label.pack(pady=5)
continue_button = Button(about_frame, text="继续翻译", command=continue_translation)
continue_button.pack( padx=10)
continue_mode_label = Label(about_frame, text="或者继续进行翻译")
continue_mode_label.pack(pady=5)



Separator(about_frame, orient='horizontal').pack(fill='x', pady=30)

about_label = Label(about_frame, text= f"软件版本\nDeeplxFile by Kevin V{config.get("version")}")
about_label.pack(pady=10)
core_label = Label(about_frame, text= f"内核版本\nDeeplx Core V{config.get("deeplx_core_version")}")
core_label.pack(pady=10)

email = Label(about_frame, text= f"i@infrost.site")
email.pack(pady=10)

update_button = Button(about_frame, text="检查更新", command=start_check)
update_button.pack()


#End of GUI
notebook.pack(padx=10, pady=10, expand=True, fill="both")
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
