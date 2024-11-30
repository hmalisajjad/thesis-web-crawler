from pathlib import Path
import threading
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options  # Correct import
from bs4 import BeautifulSoup
import logging
import os
import json
import time
from webdriver_manager.chrome import ChromeDriverManager


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

        # Initialize Selenium WebDriver
        try:
            chrome_service = Service("C:\\WebDrivers\\chromedriver-win64\\chromedriver.exe")  
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            self.driver = webdriver.Chrome(service=chrome_service, options=options)
        except Exception as e:
            self.logger.error("Failed to initialize ChromeDriver", exc_info=True)
            raise RuntimeError("Unable to initialize ChromeDriver.") from e

        # Load seed URLs
        seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "seed_urls.txt"))
        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                self.start_urls = [url.strip() for url in f.readlines() if url.strip()]
                self.logger.info(f"Loaded {len(self.start_urls)} seed URLs from {seed_path}")
        except FileNotFoundError:
            self.logger.error(f"seed_urls.txt not found at {seed_path}. No URLs will be crawled.")
            self.start_urls = []
        except Exception as e:
            self.logger.error(f"Failed to load seed URLs: {e}")
            self.start_urls = []

        # Define keywords
        self.keywords = [
            "chat", "chatbot", "live chat", "customer support", "virtual assistant",
            "Zendesk", "Intercom", "Drift", "LivePerson", "OpenAI", "Tawk", "LiveChat"
        ]

    def parse(self, response):
        """Main page parsing logic with Selenium."""
        self.logger.info(f"Parsing URL: {response.url}")
        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            title = soup.title.string.strip() if soup.title else "No Title"

            # Detect keywords and chatbots
            keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in page_source.lower()]
            detected_chatbots = []

            # Detect chatbots in iframes and script tags
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
        self.logger.info(f"Parsing iframe: {response.url}")
        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            detected_chatbots = []
            iframe_sources = [iframe.get("src", "") for iframe in soup.find_all("iframe")]

            for iframe_src in iframe_sources:
                for keyword in self.keywords:
                    if keyword.lower() in iframe_src.lower():
                        detected_chatbots.append(iframe_src)

            keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in page_source.lower()]

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


reactor_running = False


def run_crawler_in_thread():
    """
    Run the Scrapy spider in a thread-safe manner with the Twisted reactor.
    """
    global reactor_running

    # Define the output directories and files
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_file = os.path.join(base_dir, "chatbot_data.json")
    temp_file = os.path.join(base_dir, "output", "temp_chatbot_data.json")

    # Ensure the output directory exists
    output_dir = os.path.dirname(temp_file)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    def merge_data(new_data):
        """
        Merge newly crawled data with existing data, avoiding duplicates.
        """
        if os.path.exists(data_file):
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                logging.error("Invalid JSON file detected, resetting.")
                existing_data = []
        else:
            existing_data = []

        # Identify duplicates using (main_url, iframe_url) pairs
        existing_urls = {(item["main_url"], item.get("iframe_url")) for item in existing_data}
        new_data_filtered = [
            item for item in new_data
            if (item["main_url"], item.get("iframe_url")) not in existing_urls
        ]
        merged_data = existing_data + new_data_filtered

        # Save merged data back to the data file
        try:
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Failed to save merged data: {e}")

        return merged_data

    def run_spider():
        """
        Configure logging and run the Scrapy spider with proper feed settings.
        """
        configure_logging()
        runner = CrawlerRunner({
            'FEEDS': {
                temp_file: {'format': 'json', 'encoding': 'utf8', 'store_empty': False, 'indent': 4},
            },
        })

        @defer.inlineCallbacks
        def crawl():
            yield runner.crawl(MultiFrameworkSpider)
            reactor.stop()

        # Handle reactor safely and disable signal handlers in multi-threading
        if not reactor.running:
            reactor.callWhenRunning(crawl)
            reactor.run(installSignalHandlers=False)

    def background_task():
        """
        Run the spider and handle merging results in a background thread.
        """
        try:
            run_spider()

            # Merge data if the temporary file exists
            if os.path.exists(temp_file):
                with open(temp_file, "r", encoding="utf-8") as f:
                    new_data = json.load(f)
                os.remove(temp_file)  # Remove temp file after processing
                return merge_data(new_data)
        except Exception as e:
            logging.error(f"Error during spider execution: {e}")
        finally:
            global reactor_running
            reactor_running = False

    # Start the crawler in a background thread
    if not reactor_running:
        reactor_running = True
        threading.Thread(target=background_task, daemon=True).start()

