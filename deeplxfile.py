import threading
import subprocess
import sys
import os
import time
from Lib import compose, data_process, extract

# 定义线程任务，执行 deeplx_windows_amd64.exe
def run_deeplx():
    exe_path = os.path.join("Lib", "deeplx_windows_amd64.exe")
    
    try:
        # 使用 subprocess 调用可执行文件
        subprocess.run([exe_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running deeplx_windows_amd64.exe: {e}")
    except FileNotFoundError:
        print(f"The file {exe_path} was not found.")

def loop():
    # 定义语言列表
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

    # 显示语言选项
    print("请输入源文件语言(数字序号,按回车结束）:")
    for i, (lang_name, _) in enumerate(languages, start=1):
        print(f" {i}. {lang_name}")

    # 接收用户输入
    source_lang_num = int(input())

    # 检查输入是否有效
    if 1 <= source_lang_num <= len(languages):
        source_lang = languages[source_lang_num - 1][1]
        print(f"你选择的语言代码是: {source_lang}")
    else:
        print("输入无效，请输入有效的数字序号。")

    # 选择目标语言
    print("\n请输入目标文件语言(数字序号):")
    for i, (lang_name, _) in enumerate(languages, start=1):
        print(f" {i}. {lang_name}")

    target_lang_num = int(input())

    if 1 <= target_lang_num <= len(languages):
        target_lang = languages[target_lang_num - 1][1]
        print(f"你选择的目标语言代码是: {target_lang}")
    else:
        print("输入无效，请输入有效的数字序号。")

    print("等待选择文件...")
    # 创建解压线程
    extract_thread = threading.Thread(target=extract.extract_file())
    extract_thread.start()
    extract_thread.join()
    
    print("完成解压")
    data_process.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
    print(f"完成翻译,正在回写{extract.input_path}")
    
    #生成翻译文件
    compose.compose_file(extract.file_type, extract.input_path)

    print("更新完成！已在输入的相同目录下生成文件")
    print("DeeplxFile by Kevin, 项目地址https://github.com/infrost/deeplxfile, Version V0.1.0")
    input("Enter键继续翻译...")
    loop()


def main():
    # 创建并启动线程
    deeplx_thread = threading.Thread(target=run_deeplx)
    deeplx_thread.start()
    print("正在启动deeplx引擎")
    # 给 deeplx 一些时间来启动
    time.sleep(1)
    loop()



if __name__ == "__main__":
    main()
