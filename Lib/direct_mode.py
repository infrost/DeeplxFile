import requests
import time
import os
output_dir = './out'
os.makedirs(output_dir, exist_ok=True)

def count_words(line):
    # 统计一行中的词数，以空格分隔
    return len(line.split())

def process_file(file_path, source_lang, target_lang):
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
    #source_lang = "EN"
    with open('./out/translated_result.txt', 'w', encoding='utf-8') as result_file:
        process_block_count = 1
        for s in strings_array:
            print(f"正在处理第{process_block_count}个块...")
            process_block_count = process_block_count + 1
            s_lines = s.splitlines()  # 将多行字符串分割成行列表
            payload_texts = [{"text": line, "requestAlternatives": 0, "source_lang": source_lang} 
                            for line in enumerate(s_lines)]
            #print(payload_texts)
            ## 构造请求头
            url = "https://www2.deepl.com/jsonrpc"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
            payload = {
                "jsonrpc": "2.0",
                "method": "LMT_handle_texts",
                "params": {
                    "texts": payload_texts,
                    "lang": {
                        "source_lang": source_lang,  # 指定源语言
                        "target_lang": target_lang
                    },
                    "priority": 1,
                    "commonJobParams": {},
                    "timestamp": int(time.time() * 1000)
                }
            }


            max_retries = 5
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    print("正在等待返回结果")
                    if response.status_code == 200:
                        result_origin = response.json()
                        #print(f"收到返回值\n{result_origin}\n")

                        # 处理所有结果并去掉 index
                        for item in result_origin['result']['texts']:
                            # 去掉前面的 index（假设格式始终是 "index: 内容"）
                            text = item['text'] 
                            result_file.write(text + '\n')

                        success = True

                    else:
                        raise ValueError("未找到返回数据，可能是因为请求过于频繁，程序将会尝试重试")

                except (requests.exceptions.RequestException, ValueError) as exc:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Error occurred: {exc}. Retrying in 10 seconds... ({retry_count}/{max_retries})")
                        time.sleep(10)
                    else:
                        print(f"Failed after {max_retries} retries. Moving on to the next string.")

            if not success:
                error_lines = s.splitlines()
                error_messages = [f"Error: {error_line}" for error_line in error_lines]
                error_message = "\n".join(error_messages) + "\n"
                result_file.write(error_message)
                print(f"Failed after {max_retries} retries. Moving on to the next string.")