import os
import json

# 定义默认配置
default_config = {
    "save_original": False, #保留原文件值
    "version": "0.5.11",
    "dev": False,
    "i18n": "ZH",
    "playwright_headless": False,
    "playwright_path": "./Lib/Webkit/Playwright.exe", # Mac "./Lib/Webkit/pw_run.sh", windows "./Lib/Webkit/Playwright.exe"
    "browser_login": False,
    "force_lang_select": False,
    "translation_mode": "playwright",
    "disable_user_profile": False,
    "enhance_mode": False,
    "deepl_token": "",
    "deeplx_core_version": "1.0.4",
    "deeplx_server": "",
    "llm_api_base": "https://api.openai.com/v1",
    "llm_api_key": "",
    "llm_model": "gpt-4o",
    "llm_prompt": "",
    "llm_max_token":"4096"
}

# 定义配置文件的路径
config_path = './config.json'

def load_config():
    """加载配置，如果config.json不存在则创建并使用默认配置。"""
    if not os.path.exists(config_path):
        # 如果不存在，创建config.json并写入默认配置
        with open(config_path, 'w', encoding='utf-8') as config_file:
            json.dump(default_config, config_file, indent=4)
        return default_config
    else:
        # 如果存在，加载config.json并更新默认配置
        with open(config_path, 'r', encoding='utf-8') as config_file:
            user_config = json.load(config_file)
        # 更新默认配置
        return {**default_config, **user_config}

def save_config(config):
    """将配置保存到config.json中"""
    with open(config_path, 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file, indent=4)

# 直接加载配置供外部使用
config = load_config()
