from playwright.sync_api import sync_playwright
import time

def force_lang_select(target_lang):
    with sync_playwright() as p:
        browser = p.webkit.launch(executable_path="./webkit/Playwright.exe", headless=False)
        page = browser.new_page()
        
        # 打开 Deepl 翻译器网页
        page.goto("https://www.deepl.com/en/translator")
        
        time.sleep(1)  # 等待选择区域展开
        # 点击目标语言选择区域
        page.wait_for_selector('div[data-testid="translator-target-lang"]')
        page.click('div[data-testid="translator-target-lang"]')
        print("已点击语言选择区域")


        # 使用 XPath 选择器
        lang_xpath = f'//button[@data-testid="translator-lang-option-{target_lang}"]'
        page.wait_for_selector(lang_xpath)
        page.click(lang_xpath)

        print(f"已强制指定目标语言{target_lang}")


force_lang_select("zh-Hant")


