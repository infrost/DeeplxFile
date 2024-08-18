import os
import json

# 定义默认配置
default_config = {
    "save_original": False, #保留原文件值
    "version": "0.1.1",
    "dev": False,
    "direct_mode": False
}

# 定义配置文件的路径
config_path = './config.json'

def load_config():
    """加载配置，如果config.json不存在则创建并使用默认配置。"""
    if not os.path.exists(config_path):
        # 如果不存在，创建config.json并写入默认配置
        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        return default_config
    else:
        # 如果存在，加载config.json并更新默认配置
        with open(config_path, 'r') as config_file:
            user_config = json.load(config_file)
        # 更新默认配置
        return {**default_config, **user_config}

def save_config(config):
    """将配置保存到config.json中"""
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

# 直接加载配置供外部使用
config = load_config()
