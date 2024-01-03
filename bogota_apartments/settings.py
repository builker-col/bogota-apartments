# Scrapy settings for bogota_apartments project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from dotenv import load_dotenv
import os

load_dotenv()

BOT_NAME = 'bogota_apartments'

SPIDER_MODULES = ['bogota_apartments.spiders']
NEWSPIDER_MODULE = 'bogota_apartments.spiders'

VERSION = '2.0.0'

# Splash settings
SPLASH_URL = 'http://localhost:8050/'  # send requests to render web pages and execute JavaScript code.
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'  # dupe filter is a mechanism that prevents Scrapy from making duplicate requests to a website. 
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage' # stores the cache on the local file system

# Database settings - uncomment if you want to use MongoDB
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DATABASE = os.getenv('MONGO_DATABASE')

if not os.getenv('MONGO_COLLECTION_RAW') or not os.getenv('MONGO_COLLECTION_PROCESSED'):
    MONGO_COLLECTION_RAW = 'scrapy_bogota_apartments'
    MONGO_COLLECTION_PROCESSED = 'scrapy_bogota_apartments_processed'
    
else:
    MONGO_COLLECTION_RAW = os.getenv('MONGO_COLLECTION_RAW')
    MONGO_COLLECTION_PROCESSED = os.getenv('MONGO_COLLECTION_PROCESSED')

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "bogota_apartments (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "bogota_apartments.middlewares.BogotaApetmentsSpiderMiddleware": 543,

# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = { 
    'scrapy_splash.SplashCookiesMiddleware': 723,  # This middleware handles cookies in requests made to Splash, and it is assigned the priority of 723
    'scrapy_splash.SplashMiddleware': 725,  # This middleware provides the integration between Scrapy and Splash and is assigned the priority of 725.
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,  # This middleware is responsible for handling HTTP compression, and it is assigned the priority of 810.
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    # 'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'bogota_apartments.pipelines.MongoDBPipeline': 500 # uncomment if you want to use MongoDB
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'

# Logging settings
# LOG_STDOUT = True
# LOG_FILE = f'logs/scrapy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
# LOG_LEVEL = 'DEBUG'