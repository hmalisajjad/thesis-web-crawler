import scrapy
from scrapy.crawler import CrawlerProcess
# from twisted.internet import reactor, defer
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
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react
# import threading

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
        title = response.css('title::text').get()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # chatbot_elements = ""
        chatbot_elements = soup.find_all(class_=lambda x: x and any(keyword.lower() in x.lower() for keyword in self.keywords))

        chatbots = [str(el) for el in chatbot_elements]
        keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in response.text.lower()]

        iframes = soup.find_all('iframe')
        # iframe_chatbots = []
        for iframe in iframes:
            iframe_src = iframe.get('src')
            if iframe_src:
                # Scrapy will fetch the iFrame content as a new request
                request = response.follow(iframe_src, self.parse_iframe)
                request.meta['main_url'] = url  # Pass the main URL for reference
                yield request

        metadata = {
            "url": url,
            "title": title,
            "detected_chatbots": chatbots,
            "keywords_detected": keywords_detected,
            "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        yield metadata
    
    def parse_iframe(self, response):
        """Parse iFrame content to detect chatbots."""
        main_url = response.meta.get('main_url')  # Get the main page URL for reference
        iframe_url = response.url
        soup = BeautifulSoup(response.text, 'html.parser')

        # Detect chatbot elements within the iFrame content
        iframe_chatbot_elements = soup.find_all(class_=lambda x: x and any(
            keyword.lower() in x.lower() for keyword in self.keywords))
        iframe_chatbots = [str(el) for el in iframe_chatbot_elements]
        iframe_keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in response.text.lower()]

        # Compile metadata for the iFrame
        iframe_metadata = {
            "main_url": main_url,
            "iframe_url": iframe_url,
            "detected_chatbots": iframe_chatbots,
            "keywords_detected": iframe_keywords_detected,
            "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        yield iframe_metadata
        
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
    configure_logging()

    # Define the absolute path for chatbot_data.json
    data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chatbot_data.json"))
    logging.info(f"Data will be saved to: {data_file_path}")

    # Use CrawlerProcess to handle the reactor lifecycle automatically
    process = CrawlerProcess({
        'FEEDS': {
            data_file_path: {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
            },
        },
    })

    # Start the crawl and block until it's finished
    logging.info("Starting the crawl process.")
    process.crawl(MultiFrameworkSpider)
    process.start()  # Blocks until crawling is finished
    logging.info("Crawl process completed.")

    # Load the data from the output file
    if os.path.exists(data_file_path):
        with open(data_file_path, "r") as f:
            try:
                data = json.load(f)
                logging.info("Data successfully loaded from file.")
                return data
            except json.JSONDecodeError as e:
                logging.error(f"Error loading JSON data: {e}")
                return None
    else:
        logging.error("chatbot_data.json not found after crawling.")
        return None

# def run_crawler_in_thread():
#     def run():
#         process = CrawlerRunner({
#             'FEEDS': {
#                 'chatbot_data.json': {
#                     'format': 'json',
#                     'encoding': 'utf8',
#                     'store_empty': False,
#                     'indent': 4,
#                 },
#             },
#         })

#         @inlineCallbacks
#         def crawl():
#             yield process.crawl(MultiFrameworkSpider)
#             reactor.stop()

#         crawl()
#         reactor.run()

#     thread = threading.Thread(target=run)
#     thread.start()
#     thread.join()

#     # Load data from the output file
#     data_path = os.path.join(os.path.dirname(__file__), "..", "..", "chatbot_data.json")
#     if os.path.exists(data_path):
#         with open(data_path, "r") as f:
#             data = json.load(f)
#         return data
#     else:
#         logging.error("chatbot_data.json not found after crawling.")
#         return None