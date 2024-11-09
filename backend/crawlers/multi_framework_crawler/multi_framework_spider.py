import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os
import json
from idna.core import InvalidCodepoint  # Import InvalidCodepoint for specific error handling

class MultiFrameworkSpider(scrapy.Spider):
    name = "multi_framework_spider"
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'ChatbotCrawler (+http://localhost)',
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DEPTH_LIMIT': 3,
    }

    def __init__(self, *args, **kwargs):
        super(MultiFrameworkSpider, self).__init__(*args, **kwargs)
        
        # Load seed URLs from seed_urls.txt
        seed_path = os.path.join(os.path.dirname(__file__), '..', '..', 'seed_urls.txt')
        if os.path.exists(seed_path):
            with open(seed_path, 'r') as f:
                self.start_urls = [url.strip() for url in f.readlines() if url.strip()]
        else:
            logging.error("seed_urls.txt not found.")
            self.start_urls = []

        # Define keywords to look for on the pages
        self.keywords = ["chat", "chatbot", "live chat", "customer support", "virtual assistant", "Zendesk", "Intercom", "Drift", "LivePerson", "OpenAI", "ChatGPT", "GPT-3", "Bard", "Commoncrawl"]

    def parse(self, response):
        url = response.url
        logging.info("Hello There")
        logging.info("Url: " + url)
        title = response.css('title::text').get()
        logging.info("Title: " + title)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # chatbot_elements = ""
        chatbot_elements = soup.find_all(class_=lambda x: x and any(keyword.lower() in x.lower() for keyword in self.keywords))

        chatbots = [str(el) for el in chatbot_elements]
        keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in response.text.lower()]

        metadata = {
            "url": url,
            "title": title,
            "detected_chatbots": chatbots,
            "keywords_detected": keywords_detected,
            "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # # Load seed URLs from chatbot_data.json
        # f = open("chatbot_data.json", "r+")
        # f.seek(0)
        # # to erase all data  
        # f.truncate()

        yield metadata
        # try:
        #     options = webdriver.ChromeOptions()
        #     options.add_argument("--headless")
        #     with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
        #         driver.get(url)
        #         WebDriverWait(driver, 10).until(
        #             EC.presence_of_element_located((By.CLASS_NAME, "chatbot-dynamic"))
        #         )
        #         dynamic_chatbots = driver.find_elements(By.CLASS_NAME, "chatbot-dynamic")

        #         chatbots = [element.get_attribute("outerHTML") for element in dynamic_chatbots] + [str(el) for el in chatbot_elements]
        #         keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in response.text.lower()]

        #         metadata = {
        #             "url": url,
        #             "title": title,
        #             "detected_chatbots": chatbots,
        #             "keywords_detected": keywords_detected,
        #             "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
        #         }

        #         yield metadata
        # except InvalidCodepoint as e:
        #     logging.error(f"IDNA error for URL {url}: {e}")
        # except Exception as e:
        #     logging.error(f"Error in Selenium for {url}: {e}")

def run_crawler():
    # Configure logging for Scrapy
    configure_logging()

    try:
        # Initialize CrawlerRunner
        runner = CrawlerRunner({
            'FEEDS': {
                'chatbot_data.json': {
                    'format': 'json',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'indent': 4,
                },
            },
        })

        # Function to start the crawl
        @defer.inlineCallbacks
        def crawl():
            yield runner.crawl(MultiFrameworkSpider)
            reactor.stop()

        # Run the crawl
        crawl()
        reactor.run()  # This will block until the crawling is finished

        # Verify if data was written to chatbot_data.json
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "chatbot_data.json")
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                data = json.load(f)
            return data
        else:
            logging.error("chatbot_data.json not found after crawling.")
            return None

    except Exception as e:
        logging.error(f"Error running the crawler: {e}", exc_info=True)
        return None


def run_crawler_test():
        # Configure logging for Scrapy
    configure_logging()

    try:
        # Initialize CrawlerRunner
        runner = CrawlerRunner({
            'FEEDS': {
                'chatbot_data.json': {
                    'format': 'json',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'indent': 4,
                },
            },
        })

        # Function to start the crawl
        @defer.inlineCallbacks
        def crawl():
            yield runner.crawl(MultiFrameworkSpider)
            reactor.stop()

        # Run the crawl
        crawl()
        reactor.run()  # This will block until the crawling is finished

        # Verify if data was written to chatbot_data.json
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "chatbot_data.json")
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                data = json.load(f)
            return data
        else:
            logging.error("chatbot_data.json not found after crawling.")
            return None

    except Exception as e:
        logging.error(f"Error running the crawler: {e}", exc_info=True)
        return None