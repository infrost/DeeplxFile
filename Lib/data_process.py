import httpx
import json
import os
import time
from Lib.config import config
output_dir = './out'
os.makedirs(output_dir, exist_ok=True)

def count_words(line):
    # 统计一行中的词数，以空格分隔
    return len(line.split())

def process_file(file_path, source_lang, target_lang, deepl_token, mode = 'w'):
    if deepl_token:
        print("deeplx方法：Pro模式，将会消耗token")
        if config.get("deeplx_server"):
            deeplx_api = f"http://{deeplx_server}/v1/translate?token=deepl_token"
        else:
            deeplx_api = "http://127.0.0.1:1188/v1/translate?token=deepl_token"
    else:
        print("deeplx方法：免费模式")
        if config.get("deeplx_server"):
            deeplx_api = f"http://{deeplx_server}/translate"
        else:
            deeplx_api = "http://127.0.0.1:1188/translate"

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
        
        if total_word_count > 1000:
            # 当前字符串超过500词，截断并保存
            strings_array.append('\n'.join(current_string))
            # 重置统计
            total_word_count = 0
            current_string = []
    
    # 添加最后一部分（如果有剩余）
    if current_string:
        strings_array.append('\n'.join(current_string))
    alternative_index = 0  # 用于命名 alternatives 文件
    with open('./out/translated_result.txt', mode, encoding='utf-8') as result_file:
        process_block_count = 1
        for s in strings_array:
            print(f"正在处理第{process_block_count}个块...")
            process_block_count = process_block_count + 1
            json_array = str(s)
            data = {
                "text": s,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
            post_data = json.dumps(data)
            print(post_data)
            input()
            retry_count = 0
            max_retries = 1
            success = False
            timeout_value = 20.0  # 秒
            retry_interval = 5.0
            while retry_count < max_retries:
                
                try:
                    print("正在向deepl服务器发送请求")
                    # 发送POST请求并打印结果
                    r = httpx.post(url=deeplx_api, data=post_data, timeout=timeout_value)
                    print("正在等待回传结果...")
                    response_data = r.json()

                    # 检查 'data' 是否存在
                    if 'data' in response_data:
                        # 保存 data 内容到 translated_result.txt
                        result_file.write(response_data['data'] + '\n')
                        result_file.flush()
                        success = True
                        print(f"收到数据 {response_data}")

                        # 如果存在 alternatives，保存每个替代到不同的文件
                        if "alternatives" in response_data and response_data["alternatives"] is not None:
                            alternatives = response_data["alternatives"]
                            #print(alternatives)
                            for alternative in alternatives:
                                with open(f'./out/alternatives({alternative_index}).txt', mode, encoding='utf-8') as alt_file:
                                    alt_file.write(alternative + '\n')
                                alternative_index += 1
                        break  # 成功处理后退出重试循环

                    else:
                        raise ValueError("未找到返回数据，可能是因为请求过于频繁，程序将会尝试重试\n 这可能是deeplx内核的问题，可以重启程序然后尝试兼容性更强的playwright模式")
                
                except (httpx.RequestError, ValueError) as exc:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"发生错误: {exc}. 程序将在{retry_interval} 秒后尝试... ({retry_count}/{max_retries})\n你可能需要切换到兼容性更强的playwright模式")
                        time.sleep(retry_interval)
                    else:
                        print(f"已达到最大尝试值： {max_retries} ，翻译失败，正在尝试下一区块翻译")
            
            if not success:
                error_lines = s.splitlines()
                error_messages = [f"Error: {error_line}" for error_line in error_lines]
                error_message = "\n".join(error_messages) + "\n"
                result_file.write(error_message)
                print(f"已达到最大尝试值： {max_retries} ，翻译失败，正在尝试下一区块翻译")


