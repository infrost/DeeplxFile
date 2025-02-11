import openai
import time
import os
import json
output_dir = './out'
os.makedirs(output_dir, exist_ok=True)

languages = {
    "zh-Hans": "中文(简体)",
    "zh-Hant": "中文(繁体)",
    "en-US": "英文(美国)",
    "en-GB": "英文(英国)",
    "ja": "日文",
    "ko": "韩文",
    "fr": "法文",
    "de": "德文",
    "ru": "俄文",
    "es": "西班牙文",
    "it": "意大利文",
    "pt": "葡萄牙文",
}

def llm_process(file_path, source_lang, target_lang, api_base, api_key, model, max_token = 4096, custom_prompt = "", mode = 'w', retries = 3, delay = 5):
    openai.api_base = api_base
    openai.api_key = api_key
    llm_prompt = custom_prompt
    target_language_name = languages.get(target_lang, target_lang)
    if llm_prompt and llm_prompt is not None:
        system_prompt = (f"你是一个翻译助手，以json格式输出。翻译要求:{llm_prompt}\n"
                         f"请将以下文本逐行翻译成语言代码为`{target_language_name}`，并确保每一行都被翻译，包括空行。"
                         "**请确保翻译前后行数完全一致，除此之外不要有多余的消息**")
    else:
        system_prompt = (f"你是一个翻译助手，以json格式输出。请将以下文本逐行翻译成语言代码为`{target_language_name}`，"
                         "并确保每一行都被翻译，包括空行。**请确保翻译前后行数完全一致，除此之外不要有多余的消息**")

    def get_response_from_model(source_data, prompt):
        messages = source_data
        print("正在向大模型发送翻译请求，可能需要一些时间...")
        for attempt in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": messages}
                    ]
                )
                return response.choices[0].message['content'].strip()
            
            except openai.error.OpenAIError as e:
                print(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Unable to get a response.")
                    return ""
            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Unable to get a response.")
                    return ""

    def convert_to_json(text):
        lines = text.split('\n')
        json_data = [{"line" + str(index + 1): line} for index, line in enumerate(lines)]
        return json.dumps(json_data, ensure_ascii=False, indent=4)

    def convert_json_to_text(json_text):
        json_data = json.loads(json_text)
        lines = [list(item.values())[0] for item in json_data]
        # 使用 join 拼接所有行
        result = "\n".join(lines)
        # 如果 JSON 的最后一行为空字符串，确保结果末尾保留换行符
        if json_data and list(json_data[-1].values())[0] == "":
            if not result.endswith("\n"):
                result += "\n"
        return result

    def split_text_into_chunks(text, max_tokens):
        # 确保 max_tokens 为整数
        if not isinstance(max_tokens, int):
            try:
                max_tokens = int(max_tokens)
            except ValueError:
                print("Invalid max_tokens value. It must be an integer.")
                return []
        # 将文本转换为 JSON 数据（列表形式）
        data = json.loads(convert_to_json(text))
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for item in data:
            item_tokens = len(json.dumps(item))
            if current_tokens + item_tokens > max_tokens:
                chunks.append(json.dumps(current_chunk, ensure_ascii=False))
                current_chunk = []
                current_tokens = 0
            current_chunk.append(item)
            current_tokens += item_tokens
        
        if current_chunk:
            chunks.append(json.dumps(current_chunk, ensure_ascii=False))
        
        return chunks
    
    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

    # 根据 max_token 限制，将文本拆分为多个块
    text_chunks = split_text_into_chunks(text, max_token)
    translated_text = ""
    
    for i, chunk in enumerate(text_chunks):
        translated_chunk = get_response_from_model(chunk, system_prompt)
        if translated_chunk:
            print(translated_chunk)
            # 如果是最后一个块，则不额外添加换行符
            if i == len(text_chunks) - 1:
                translated_text += convert_json_to_text(translated_chunk)
            else:
                translated_text += convert_json_to_text(translated_chunk) + '\n'
        else:
            print("Skipping chunk due to translation failure.")
    
    if not translated_text:
        print("No translation results available.")
        return ""

    try:
        with open('./out/translated_result.txt', mode, encoding='utf-8') as output_file:
            output_file.write(translated_text)
        print("Translation complete.")
    except Exception as e:
        print(f"Error writing to file: {e}")
        return ""
