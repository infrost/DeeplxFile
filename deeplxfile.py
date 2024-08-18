import threading
import subprocess
import sys
import os
import time
from Lib import compose, data_process, extract, direct_mode
from Lib.config import config

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
    while True:
        # 显示语言选项
        print("请输入源文件语言(数字序号,按回车结束）:\n 输入0取消")
        for i, (lang_name, _) in enumerate(languages, start=1):
            print(f" {i}. {lang_name}")

        # 接收用户输入
        source_lang_num = int(input())

        # 检查输入是否有效
        if 1 <= source_lang_num <= len(languages):
            source_lang = languages[source_lang_num - 1][1]
            #print(f"你选择的语言代码是: {source_lang}")
        elif source_lang_num == 0:
            print("已取消")
            continue
        else:
            print("输入无效，请输入有效的数字序号。")
            continue

        # 选择目标语言
        print("\n请输入目标文件语言(数字序号):\n 输入0取消")
        #for i, (lang_name, _) in enumerate(languages, start=1):
        #    print(f" {i}. {lang_name}")

        target_lang_num = int(input())

        if 1 <= target_lang_num <= len(languages):
            target_lang = languages[target_lang_num - 1][1]
            #print(f"你选择的目标语言代码是: {target_lang}")
        elif target_lang_num == 0:
            print("已取消")
            continue
        else:
            print("输入无效，请输入有效的数字序号。")
            continue

        print("等待选择文件...")
        try:
            # 创建解压线程
            extract_thread = threading.Thread(target=extract.extract_file)
            extract_thread.start()
            extract_thread.join()
        except Exception as e:
            # 如果线程启动失败，捕获异常并将direct_mode设置为True
            print(f"Deeplx引擎异常，尝试使用直连模式 {e}")
            config['direct_mode'] = True
            save_config(config)
            print("已将direct_mode设置为True")
        if extract.process_cancelled:
            print ("文件导入取消")
            continue
        print("完成解压")
        if config.get("direct_mode", False):
            direct_mode.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
        else:
            data_process.process_file('./tmp/text_extracted.txt', source_lang, target_lang)
            print(f"完成翻译,正在回写{extract.input_path}")
        
        #生成翻译文件
        compose.compose_file(extract.file_type, extract.input_path)

        print("更新完成！已在输入的相同目录下生成文件")
        print(f"DeeplxFile V0.2.0 by Kevin, 项目地址https://github.com/infrost/deeplxfile")
        input("Enter键继续翻译...")


def main():
    # 创建并启动线程
    if config.get("direct_mode", False):
        print("使用直连模式请求deepl的翻译返回，不使用deeplx引擎，如果频繁请求可能会遇到错误\n该模式只能翻译较小的文件，大文件请使用deeplx引擎\n在config.json中direct_mode项设置是否直连")
    else:
        deeplx_thread = threading.Thread(target=run_deeplx)
        deeplx_thread.start()
        print("正在启动deeplx引擎")
    # 给 deeplx 一些时间来启动
    time.sleep(1)
    loop()



if __name__ == "__main__":
    main()
