# Author: Erik Garcia (@erik172)
# Version: Developer
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import json

# Scrapy
import scrapy


class LahausSpider(scrapy.Spider):
    name = "lahaus"
    allowed_domains = ["lahaus.com"]
    start_urls = ["https://www.lahaus.com/buscar?locations=bogota"]

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--start-maximized')  # Opcional: para abrir el navegador maximizado
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def parse(self, response):
        time.sleep(5)
        self.driver.get(response.url)
        print(response.body)
        time.sleep(5)
        pass
