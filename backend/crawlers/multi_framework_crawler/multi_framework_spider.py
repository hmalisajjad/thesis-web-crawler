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
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging
from html import unescape
import os
import json
import time
from threading import Lock
from urllib.parse import urlparse, urlunparse

import shutil

# Global toggle for Selenium usage
selenium_enabled = True


def enable_selenium(state: bool):
    """Enable or disable Selenium for crawling."""
    global selenium_enabled
    selenium_enabled = state


def normalize_url(url):
    """Normalize URLs for consistent deduplication."""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))


def clear_cache():
    """Clear HTTP cache."""
    cache_dir = Path(__file__).parent.parent.parent / "httpcache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    logging.info("Cache cleared.")

class MultiFrameworkSpider(scrapy.Spider):
    name = "multi_framework_spider"
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'ChatbotCrawler (+http://localhost)',
        'DOWNLOAD_DELAY': 0.2,  # Reduced delay for faster crawling
        'CONCURRENT_REQUESTS': 8,  # Increased concurrency
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'DEPTH_LIMIT': 3,
        'HTTPCACHE_ENABLED': True,  # Enable HTTP caching to reduce duplicate requests
        'LOG_LEVEL': 'WARNING',  # Change log level to WARNING
    }

    def __init__(self, urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited_iframe_urls = set()
        self.visited_chatbot_urls = set()

        try:
            self.logger.info("Initializing ChromeDriver...")
            chrome_service = Service("C:\\WebDrivers\\chromedriver-win64\\chromedriver.exe")
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-web-security")
            options.add_argument("--ignore-ssl-errors")  # Ignore SSL errors
            options.add_argument("--ignore-certificate-errors")  # Ignore certificate errors
            options.add_argument("--disable-software-rasterizer")  # Fix pixel format errors
            options.add_argument("--enable-unsafe-swiftshader")  # Swiftshader fallback for rendering
            self.driver = webdriver.Chrome(service=chrome_service, options=options)
        except Exception as e:
            self.logger.error("Failed to initialize ChromeDriver", exc_info=True)
            raise RuntimeError("Unable to initialize ChromeDriver.") from e

        if urls:
            self.start_urls = urls
        else:
            # Load from seed file
            seed_path = Path(__file__).parent.parent.parent / "seed_urls.txt"
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    self.start_urls = [url.strip() for url in f.readlines() if url.strip()]
                    self.logger.info(f"Loaded {len(self.start_urls)} seed URLs from {seed_path}")
            except FileNotFoundError:
                self.logger.error(f"Seed file not found at {seed_path}. No URLs will be crawled.")
                self.start_urls = []
            except Exception as e:
                self.logger.error(f"Error loading seed URLs: {e}")
                self.start_urls = []

        self.keywords = [
            "chat", "chatbot", "live chat", "customer support", "virtual assistant",
            "Zendesk", "Intercom", "Drift", "OpenAI", "Tawk", "LiveChat", "Tawk.to",
            "Botpress", "Dialogflow", "Watson Assistant", "HubSpot", "Kommunicate",
            "Communication", "conversational bot", "Microsoft Bot Framework",
            "bot.js", "chatbot.js", "chat-widget", "livechat.min.js", "webchat"
        ]
        self.visited_urls = set()

    def parse(self, response):
        normalized_url = normalize_url(response.url)
        if normalized_url in self.visited_urls:
            self.logger.warning(f"Skipping already visited URL: {normalized_url}")
            return
        self.visited_urls.add(normalized_url)

        self.logger.warning(f"Parsing URL: {normalized_url}")
        try:
            if selenium_enabled:
                self.driver.get(response.url)
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(5)
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
            else:
                soup = BeautifulSoup(response.body, "html.parser")

            # Extract body text for keyword matching
            body_text = soup.get_text(separator=' ').lower()

            # Detect keywords
            keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in body_text]

            # Detect chatbots by extracting iframe elements and checking their `src`
            detected_chatbots = set()
            for iframe in soup.find_all("iframe", src=True):
                iframe_src = iframe.get("src", "").strip()
                if not iframe_src.startswith("javascript:"):
                    normalized_iframe_src = normalize_url(iframe_src)
                    if normalized_iframe_src not in self.visited_iframe_urls:
                        self.visited_iframe_urls.add(normalized_iframe_src)
                        detected_chatbots.add(normalized_iframe_src)

                        # Yield a request to the iframe URL, which will be handled by `parse_iframe`
                        yield scrapy.Request(
                            url=iframe_src,
                            callback=self.parse_iframe,
                            meta={
                                'main_url': normalized_url,
                                'main_title': soup.title.string.strip() if soup.title else "No Title"
                            }
                        )

            # Detect unconventional chatbot structures
            for div in soup.find_all("div", class_="chat-widget"):
                data_api = div.get("data-api")
                if data_api and data_api not in detected_chatbots:
                    detected_chatbots.add(data_api)

            # Additional detection in inline scripts
            for script in soup.find_all("script"):
                if script.string and any(keyword.lower() in script.string.lower() for keyword in self.keywords):
                    self.logger.debug(f"Detected chatbot-related keyword in script tag.")
                    detected_chatbots.add(normalized_url)

            # Debug logging
            self.logger.debug(f"Detected keywords: {keywords_detected}")
            self.logger.debug(f"Detected chatbots in {normalized_url}: {list(detected_chatbots)}")

            yield {
                "main_url": normalized_url,
                "title": soup.title.string.strip() if soup.title else "No Title",
                "iframe_url": None,
                "detected_chatbots": list(detected_chatbots),
                "keywords_detected": keywords_detected,
                "date_collected": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            self.logger.error(f"Error parsing {normalized_url}: {e}")


    def parse_iframe(self, response):
        normalized_url = normalize_url(response.url)
        if normalized_url in self.visited_iframe_urls:
            self.logger.warning(f"Skipping already visited iframe: {normalized_url}")
            return
        self.visited_iframe_urls.add(normalized_url)

        self.logger.warning(f"Parsing iframe: {normalized_url}")
        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            detected_chatbots = set()

            # Detect chatbots through iframes, including hidden iframes
            iframe_sources = [iframe.get("src", "").strip() for iframe in soup.find_all("iframe")]
            for iframe_src in iframe_sources:
                if iframe_src.startswith("javascript:"):
                    self.logger.warning(f"Ignoring invalid iframe src: {iframe_src}")
                    continue
                normalized_iframe_src = normalize_url(iframe_src)
                if normalized_iframe_src not in self.visited_iframe_urls:
                    self.visited_iframe_urls.add(normalized_iframe_src)
                    detected_chatbots.add(normalized_iframe_src)

            # Detect keywords in page source
            keywords_detected = [keyword for keyword in self.keywords if keyword.lower() in page_source.lower()]

            self.logger.debug(f"Detected keywords in iframe {normalized_url}: {keywords_detected}")
            self.logger.debug(f"Detected chatbots in iframe {normalized_url}: {list(detected_chatbots)}")

            yield {
                "main_url": response.meta.get("main_url"),
                "title": response.meta.get("main_title"),
                "iframe_url": normalized_url,
                "detected_chatbots": list(detected_chatbots),
                "keywords_detected": keywords_detected,
                "date_collected": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            self.logger.error(f"Error parsing iframe {normalized_url}: {e}")

    def closed(self, reason):
        """Close WebDriver when the spider stops."""
        self.driver.quit()
        self.logger.warning(f"Spider closed: {reason}")

reactor_lock = Lock()

reactor_running = False

def run_crawler_in_thread(urls=None):
    """Run the Scrapy spider in a thread-safe manner."""
    global reactor_running
    with reactor_lock:
        if reactor_running:
            logging.warning("Reactor already running. Skipping...")
            return

        reactor_running = True

    base_dir = Path(__file__).parent.parent.parent
    data_file = base_dir / "chatbot_data.json"
    temp_file = base_dir / "output" / "temp_chatbot_data.json"
    temp_file.parent.mkdir(parents=True, exist_ok=True)

    def merge_data(new_data):
        if data_file.exists():
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                logging.error("Invalid JSON file detected, resetting.")
                existing_data = []
        else:
            existing_data = []

        existing_urls = {(item["main_url"], item.get("iframe_url")) for item in existing_data}
        new_data_filtered = [
            item for item in new_data if (item["main_url"], item.get("iframe_url")) not in existing_urls
        ]
        merged_data = existing_data + new_data_filtered

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)

        return merged_data

    def run_spider():
        configure_logging()
        runner = CrawlerRunner({
            'FEEDS': {str(temp_file): {'format': 'json', 'encoding': 'utf8', 'indent': 4}}
        })

        @defer.inlineCallbacks
        def crawl():
            yield runner.crawl(MultiFrameworkSpider, urls=urls)
            reactor.stop()

        if not reactor.running:
            reactor.callWhenRunning(crawl)
            reactor.run(installSignalHandlers=False)

    def background_task():
        global reactor_running
        try:
            run_spider()
            if temp_file.exists():
                with open(temp_file, "r", encoding="utf-8") as f:
                    new_data = json.load(f)
                merge_data(new_data)
                temp_file.unlink()
        except Exception as e:
            logging.error(f"Error during spider execution: {e}")
        finally:
            with reactor_lock:
                reactor_running = False

    threading.Thread(target=background_task, daemon=True).start()
