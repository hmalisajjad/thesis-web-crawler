import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup
from twisted.internet import reactor, defer
from twisted.internet.task import react
from twisted.internet.threads import deferToThread
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

from webdriver_manager.chrome import ChromeDriverManager
print(ChromeDriverManager().install())

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
            "Zendesk", "Intercom", "Drift", "LivePerson", "OpenAI"
        ]

        # Initialize Selenium WebDriver
        chrome_service = Service("C:\\WebDrivers\\chromedriver-win64\\chromedriver.exe")  
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=chrome_service, options=options)

    def parse(self, response):
        self.logger.debug(f"Starting to parse URL: {response.url}")

        try:
            # Extract title using CSS selector
            title = response.css('title::text').get(default="No Title").strip()
            title = title.encode('utf-8', 'ignore').decode('utf-8')  # Clean up encoding issues
        except Exception as e:
            self.logger.error(f"Error extracting title from {response.url}: {e}")
            title = "No Title"

        # Detect keywords in the main HTML content
        keywords_detected = [
            keyword for keyword in self.keywords if keyword.lower() in response.text.lower()
        ]

        # Log detected keywords
        if keywords_detected:
            self.logger.info(f"Keywords detected on main page: {keywords_detected}")

        # Process iframes for further chatbot detection
        iframes = response.xpath("//iframe/@src").extract()

        if not iframes:
            self.logger.warning(f"No iframes found on {response.url}")

        for iframe_url in iframes:
            if any(skip in iframe_url for skip in ["googletagmanager", "analytics"]):
                self.logger.debug(f"Skipping iframe URL: {iframe_url}")
                continue

            absolute_url = response.urljoin(iframe_url)
            self.logger.debug(f"Found iframe URL: {absolute_url}")

            yield scrapy.Request(
                url=absolute_url,
                callback=self.parse_iframe,
                meta={"main_url": response.url},
                dont_filter=True
            )

        # Yield main page results if keywords are detected
        yield {
            "main_url": response.url,
            "iframe_url": None,
            "title": title,
            "detected_chatbots": None,
            "keywords_detected": keywords_detected,
            "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def parse_iframe(self, response):
        """Parse iframe content using Selenium and Scrapy."""
        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Extract content using BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Enhanced chatbot detection
            detected_chatbots = []
            iframe_sources = [iframe.get("src", "") for iframe in soup.find_all("iframe")]

            for iframe_src in iframe_sources:
                for keyword in ["chat", "chatbot", "live chat", "customer support", "virtual assistant", "Zendesk", "Intercom", "Drift", "Tawk", "LiveChat", "LivePerson", "dialogflow", "bot", "AI assistant"]:
                    if keyword.lower() in iframe_src.lower():
                        detected_chatbots.append(iframe_src)

            # Check page source for additional keywords
            keywords_detected = [
                keyword for keyword in self.keywords if keyword.lower() in self.driver.page_source.lower()
            ]

            self.logger.info(f"Detected chatbots: {detected_chatbots}")
            self.logger.info(f"Keywords detected: {keywords_detected}")

            yield {
                "main_url": response.meta.get("main_url"),
                "iframe_url": response.url,
                "detected_chatbots": detected_chatbots,
                "keywords_detected": keywords_detected,
                "date_collected": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error in iframe {response.url}: {e}")

    def closed(self, reason):
        """Close the Selenium WebDriver when the spider is closed."""
        self.driver.quit()
        self.logger.info(f"Spider closed: {reason}")

def run_crawler_in_thread():
    """
    Run the Scrapy spider in a separate thread, merge new crawled data with existing data,
    and avoid duplicates based on 'main_url' and 'iframe_url'.
    """
    data_file = os.path.join(os.path.dirname(__file__), "..", "..", "chatbot_data.json")
    temp_file = os.path.join(os.path.dirname(__file__), "..", "..", "temp_chatbot_data.json")  # Temporary file for new data

    result_queue = queue.Queue()  # Thread-safe queue to store the result

    def merge_data(new_data):
        """Merge new crawled data with existing data, avoiding duplicates."""
        if os.path.exists(data_file):
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                logging.error("Invalid JSON file detected, resetting the file.")
                existing_data = []  # Reset if JSON is invalid
        else:
            existing_data = []

        # Avoid duplicates based on 'main_url' and 'iframe_url'
        existing_urls = {(item["main_url"], item.get("iframe_url")) for item in existing_data}
        new_data_filtered = [
            item for item in new_data
            if (item["main_url"], item.get("iframe_url")) not in existing_urls
        ]

        # Merge new data into the existing data
        merged_data = existing_data + new_data_filtered

        # Write the merged data back to the file
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)

        logging.info(f"Data merged successfully. Total records: {len(merged_data)}")
        return merged_data

    def run_spider():
        """Run the Scrapy spider and merge the data."""
        try:
            # Configure Scrapy logging
            configure_logging()

            # Define a CrawlerRunner with feed export settings
            runner = CrawlerRunner({
                'FEEDS': {
                    temp_file: {  # Save new crawled data to a temporary file
                        'format': 'json',
                        'encoding': 'utf8',
                        'store_empty': False,
                        'indent': 4,
                    },
                },
            })

            @defer.inlineCallbacks
            def crawl():
                yield runner.crawl(MultiFrameworkSpider)
                reactor.stop()

            # Start the reactor if it's not already running
            if not reactor.running:
                reactor.callWhenRunning(crawl)
                reactor.run()

            # Read newly crawled data from the temporary file
            if os.path.exists(temp_file):
                try:
                    with open(temp_file, "r", encoding="utf-8") as f:
                        new_data = json.load(f)

                    # Merge new data with existing data
                    merged_data = merge_data(new_data)

                    # Clean up the temporary file only after successful merging
                    os.remove(temp_file)

                    # Pass the result back via the queue
                    result_queue.put(merged_data)
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to read newly crawled data: {e}")
                    result_queue.put(None)
            else:
                logging.error("Temporary data file not found after crawling.")
                result_queue.put(None)

        except Exception as e:
            logging.error(f"Error during crawling: {e}")
            result_queue.put(None)

    # Run the spider in a separate thread
    thread = threading.Thread(target=run_spider)
    thread.start()
    thread.join()  # Wait for the thread to complete

    # Retrieve the result from the queue
    try:
        result = result_queue.get(timeout=10)  # Wait for up to 10 seconds for the result
    except queue.Empty:
        logging.error("Crawling thread did not return a result.")
        result = None

    # Ensure the result is not `None`
    if result:
        logging.info("Crawling completed successfully.")
    else:
        logging.error("Crawl failed or no data found.")

    return result

