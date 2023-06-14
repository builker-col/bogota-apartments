from selenium import webdriver
from fake_useragent import UserAgent
import logging
import sys
import os

main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(main_path)

fake = UserAgent().random

def config_scrapper():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(f'user-agent={fake}')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--log-level=2')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})

    driver = webdriver.Chrome(options=chrome_options)

    return driver

def config_logger(filename: str):
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s',
        encoding='utf-8'
    )

    return logging.getLogger()

