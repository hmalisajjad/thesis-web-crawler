import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import os
import json
import time

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


def run_crawler():
    """Run the spider and handle output."""
    configure_logging()

    # Define output file path
    data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chatbot_data.json"))
    logging.info(f"Data will be saved to: {data_file_path}")

    # Configure and start the crawl
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

    logging.info("Starting the crawl process.")
    process.crawl(MultiFrameworkSpider)
    process.start()  # Blocks until crawling is finished
    logging.info("Crawl process completed.")

    # Load and return scraped data
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
