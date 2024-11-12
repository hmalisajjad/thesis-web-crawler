import os
import logging
logging.info("Settings loaded successfully.")

BOT_NAME = 'chatbot_crawler'
SPIDER_MODULES = ['crawlers.multi_framework_crawler']
NEWSPIDER_MODULE = 'crawlers.multi_framework_crawler'

USER_AGENT = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +https://www.google.com/bot.html) Safari/537.36'

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DEPTH_LIMIT = 3

# ScraperAPI configuration
SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY', '8ffff6c087fde36ed0a1c2c5cca007723')
HTTP_PROXY = f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,
    'crawlers.multi_framework_crawler.middlewares.ScraperAPIMiddleware': 543,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

DOWNLOADER_CLIENT_TLS_METHOD = "TLSv1_2"
DOWNLOADER_CLIENT_TLS_CIPHERS = 'ECDHE+AESGCM:ECDHE+CHACHA20:ECDHE+SHA256:ECDHE+SHA'
