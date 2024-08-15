"""
打开目录下text_extracted.txt
该txt格式如下：
hello word
word 0
openai
gpt
（每条string一行）

for 第i行，总共m行
统计词数 = 0
统计每行的词数（可以以空格区分，n个空格就是n+1个词）
统计词数 += i行词数
如果第i行词数>500，
截断，从1-i行生成第一个string（array）
打印
继续上面操作，直至生成完所有string（array）


"""
import httpx
import json
import os
output_dir = './out'
os.makedirs(output_dir, exist_ok=True)

deeplx_api = "http://127.0.0.1:1188/translate"
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
        
        if total_word_count > 500:
            # 当前字符串超过500词，截断并保存
            strings_array.append('\n'.join(current_string))
            # 重置统计
            total_word_count = 0
            current_string = []
    
    # 添加最后一部分（如果有剩余）
    if current_string:
        strings_array.append('\n'.join(current_string))
    alternative_index = 0  # 用于命名 alternatives 文件
    with open('./out/translated_result.txt', 'w', encoding='utf-8') as result_file:
        for s in strings_array:
            print(f"正在处理...\n{s}")
            json_array = str(s)
            data = {
                "text": s,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
            post_data = json.dumps(data)
            try:
                # 发送POST请求并打印结果
                r = httpx.post(url=deeplx_api, data=post_data)
                response_data = r.json()

                # 保存 data 内容到 translated_result.txt
                result_file.write(response_data['data'] + '\n')
                print(f"收到数据{response_data}")

                # 如果存在 alternatives，保存每个替代到不同的文件
                if "alternatives" in response_data and response_data["alternatives"] is not None :
                    alternatives = response_data["alternatives"]
                    print(alternatives)
                    for alternative in alternatives:
                        with open(f'./out/alternatives({alternative_index}).txt', 'w', encoding='utf-8') as alt_file:
                            alt_file.write(alternative + '\n')
                        alternative_index += 1

            except httpx.RequestError as exc:
                print(f"An error occurred while requesting {exc.request.url!r}.")