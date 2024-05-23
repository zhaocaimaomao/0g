###
# @Author: 招財猫猫
# @Date: 2024-05-01
# @LastEditTime: 2024-05-01
# @Description: 这是0g的领测试币的脚本，请预先在谷歌的缓存安装好过人机验证的插件和轮转ip的插件
###

import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

chromedriver_path = r'C:\Users\Administrator\anaconda3\chromedriver.exe'  # 存放chromedriver的路径
input_file_path = r'~/0g/0g_exsample.csv'  # 存放钱包地址信息的文件路径
cache_path = r'--user-data-dir=D:\chromes\faucet'  # 谷歌浏览器的缓存路径
num_process = list(range(0, 10000))  # 需要领币的钱包地址的行号


def run_selenium_chrome(cache=None, extensions=None):
    chrome_driver_path = Service(chromedriver_path)
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=en-us')
    chrome_options.add_argument('--disable-lava-moat')
    if cache:
        chrome_options.add_argument(cache)
    if extensions:
        for ex in extensions:
            chrome_options.add_extension(ex)
    global driver
    driver = webdriver.Chrome(service=chrome_driver_path, options=chrome_options)
    return driver


def checkHandles():
    handles_value = driver.window_handles
    if len(handles_value) > 1:
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        checkHandles()


df = pd.read_csv(input_file_path)
if '0g_Faucet' not in df.columns:
    df['0g_Faucet'] = None
while True:
    for i in num_process:
        if pd.isna(df['0g_Faucet'][i]):
            try:
                print(i)
                address = df['Address'][i]
                run_selenium_chrome(cache=cache_path)
                wait = WebDriverWait(driver, 30)
                checkHandles()
                driver.get('https://faucet.0g.ai/')
                time.sleep(10)
                driver.switch_to.frame(0)
                WebDriverWait(driver, 120).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@aria-checked='true']")))
                driver.switch_to.default_content()
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your wallet address']")))
                driver.find_element(By.XPATH, "//input[@placeholder='Enter your wallet address']").send_keys(address)
                wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Request AOGI Token']")))
                driver.find_element(By.XPATH, "//button[text()='Request AOGI Token']").click()
                # WebDriverWait(driver, 60).until(
                #     EC.presence_of_element_located((By.XPATH, "//h3[text()='Transaction Successful']")))
                time.sleep(10)
                df.loc[i, '0g_Faucet'] = 1
                df.to_csv(input_file_path, index=False)
            except Exception as e:
                print(e)
            finally:
                driver.quit()
