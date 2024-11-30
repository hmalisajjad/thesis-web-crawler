import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup
from twisted.internet import reactor, defer
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import os
import json
import time
import queue
from urllib.parse import urlparse, urlunparse

from webdriver_manager.chrome import ChromeDriverManager


def normalize_url(url):
    """Normalize a URL by removing query parameters and fragments."""
    try:
        parsed = urlparse(url)
        # Remove query and fragment
        normalized = urlunparse(parsed._replace(query="", fragment=""))
        return normalized
    except Exception as e:
        logging.error(f"Error normalizing URL {url}: {e}")
        return url


class ChatbotDetectionSpider(scrapy.Spider):
    name = "chatbot_detection_spider"
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'ChatbotCrawler (+http://localhost)',
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DEPTH_LIMIT': 3,
    }

    def __init__(self, *args, **kwargs):
        super(ChatbotDetectionSpider, self).__init__(*args, **kwargs)

        # Load seed URLs from seed_urls.txt
        seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "seed_urls.txt"))
        if os.path.exists(seed_path):
            with open(seed_path, 'r', encoding="utf-8") as f:
                self.start_urls = [url.strip() for url in f.readlines() if url.strip()]
            self.logger.info(f"Loaded {len(self.start_urls)} seed URLs from {seed_path}")
        else:
            self.logger.error("seed_urls.txt not found.")
            self.start_urls = []

        # Define keywords to look for on the pages
        self.keywords = [
            "chat", "chatbot", "live chat", "customer support", "virtual assistant",
            "Zendesk", "Intercom", "Drift", "OpenAI", "Tawk", "LiveChat", "Tawk.to", "Botpress", "Dialogflow", "Watson Assistant", "HubSpot", "Kommunicate", "Communication", "conversational bot", "Microsoft Bot Framework","bot.js", "chatbot.js", "chat-widget", "livechat.min.js", "webchat"
        ]

        # Initialize Selenium WebDriver
        chrome_service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=chrome_service, options=options)

        # Set to store processed iframe URLs
        self.processed_iframe_urls = set()

    def parse(self, response):
        """Main page parsing logic with Selenium."""
        self.logger.debug(f"Parsing URL: {response.url}")
        self.driver.get(response.url)

        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            title = soup.title.string.strip() if soup.title else "No Title"

            # Detect keywords in the page content
            keywords_detected = [
                keyword for keyword in self.keywords if keyword.lower() in page_source.lower()
            ]

            # Detect chatbots in iframes and script tags
            detected_chatbots = []
            iframes = soup.find_all("iframe")
            scripts = soup.find_all("script")

            for iframe in iframes:
                src = iframe.get("src", "")
                if any(keyword.lower() in src.lower() for keyword in self.keywords):
                    detected_chatbots.append(src)

            for script in scripts:
                src = script.get("src", "")
                if any(keyword.lower() in src.lower() for keyword in self.keywords):
                    detected_chatbots.append(src)

            # Yield main page data
            yield {
                "main_url": response.url,
                "title": title,
                "iframe_url": None,
                "detected_chatbots": detected_chatbots,
                "keywords_detected": keywords_detected,
                "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            # Process iframes for chatbot detection
            for iframe in iframes:
                iframe_src = iframe.get("src", "")
                if iframe_src:
                    normalized_src = normalize_url(iframe_src)
                    if normalized_src in self.processed_iframe_urls:
                        self.logger.debug(f"Duplicate iframe skipped: {iframe_src}")
                        continue
                    self.processed_iframe_urls.add(normalized_src)

                    absolute_url = response.urljoin(iframe_src)
                    yield scrapy.Request(
                        url=absolute_url,
                        callback=self.parse_iframe,
                        meta={"main_url": response.url, "main_title": title},
                        dont_filter=True
                    )

        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {e}")

    def parse_iframe(self, response):
        """Parse iframe content with Selenium."""
        self.logger.debug(f"Parsing iframe: {response.url}")
        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Detect chatbots and keywords in the iframe
            detected_chatbots = []
            iframe_sources = [iframe.get("src", "") for iframe in soup.find_all("iframe")]

            for iframe_src in iframe_sources:
                for keyword in self.keywords:
                    if keyword.lower() in iframe_src.lower():
                        detected_chatbots.append(iframe_src)

            keywords_detected = [
                keyword for keyword in self.keywords if keyword.lower() in page_source.lower()
            ]

            yield {
                "main_url": response.meta.get("main_url"),
                "title": response.meta.get("main_title"),
                "iframe_url": response.url,
                "detected_chatbots": detected_chatbots,
                "keywords_detected": keywords_detected,
                "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error parsing iframe {response.url}: {e}")

    def closed(self, reason):
        """Close Selenium WebDriver when the spider stops."""
        self.driver.quit()
        self.logger.info(f"Spider closed: {reason}")


def merge_data(new_data):
    """Merge new crawled data with existing data, avoiding duplicates."""
    data_file = os.path.join(os.path.dirname(__file__), "..", "..", "chatbot_data.json")
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            logging.error("Invalid JSON file detected, resetting the file.")
            existing_data = []
    else:
        existing_data = []

    # Normalize URLs for deduplication
    existing_urls = {(normalize_url(item["main_url"]), normalize_url(item.get("iframe_url"))) for item in existing_data}
    new_data_filtered = [
        item for item in new_data
        if (normalize_url(item["main_url"]), normalize_url(item.get("iframe_url"))) not in existing_urls
    ]

    merged_data = existing_data + new_data_filtered
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    logging.info(f"Data merged successfully. Total records: {len(merged_data)}")
    return merged_data


def run_crawler_in_thread():
    """Run the Scrapy spider in a separate thread with data merging."""
    temp_file = os.path.join(os.path.dirname(__file__), "..", "..", "temp_chatbot_data.json")
    result_queue = queue.Queue()

    def run_spider():
        configure_logging()
        runner = CrawlerRunner({'FEEDS': {temp_file: {'format': 'json', 'encoding': 'utf8', 'store_empty': False}}})

        @defer.inlineCallbacks
        def crawl():
            yield runner.crawl(ChatbotDetectionSpider)
            reactor.stop()

        if not reactor.running:
            reactor.callWhenRunning(crawl)
            reactor.run()

        if os.path.exists(temp_file):
            try:
                with open(temp_file, "r", encoding="utf-8") as f:
                    new_data = json.load(f)
                merged_data = merge_data(new_data)
                os.remove(temp_file)
                result_queue.put(merged_data)
            except Exception as e:
                logging.error(f"Error processing temp data: {e}")
                result_queue.put(None)
        else:
            result_queue.put(None)

    thread = threading.Thread(target=run_spider)
    thread.start()
    thread.join()

    try:
        return result_queue.get(timeout=10)
    except queue.Empty:
        logging.error("Crawling thread timed out.")
        return None


if __name__ == "__main__":
    run_crawler_in_thread()