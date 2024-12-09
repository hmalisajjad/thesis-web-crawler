from multiprocessing import Process
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import (
    run_crawler_in_thread, enable_selenium, clear_cache
)
import logging
from pathlib import Path
import unittest
import time

# Static Websites (Simple, chatbot-related content)
STATIC_WEBSITES = [
    "https://www.wotnot.io",
    "https://www.livechat.com",
]

# Dynamic Websites (Chatbots embedded with dynamic content)
DYNAMIC_WEBSITES = [
    "https://www.tidio.com",
    "https://www.zendesk.com/chat",
]

# JavaScript-Heavy Websites (Complex chatbot structures)
JAVASCRIPT_HEAVY_WEBSITES = [
    "https://www.intercom.com",
    "https://drift.com",
]

# Define a global function for crawling
def crawl_task(urls):
    """Run the crawler in a separate process."""
    run_crawler_in_thread(urls)

class TestEfficiency(unittest.TestCase):
    def time_crawl(self, urls):
        """Helper function to measure crawl time."""
        process = Process(target=crawl_task, args=(urls,))
        process.start()
        start_time = time.time()
        process.join()  
        end_time = time.time()
        return end_time - start_time

    def test_static_website_efficiency(self):
        duration = self.time_crawl(STATIC_WEBSITES)
        self.assertLess(duration, 30, "Static websites took too long to crawl")

    def test_dynamic_website_efficiency(self):
        duration = self.time_crawl(DYNAMIC_WEBSITES)
        self.assertLess(duration, 60, "Dynamic websites took too long to crawl")

    def test_js_heavy_website_efficiency(self):
        duration = self.time_crawl(JAVASCRIPT_HEAVY_WEBSITES)
        self.assertLess(duration, 90, "JavaScript-heavy websites took too long to crawl")


    def test_selenium_impact(self):
        """Measure the time taken with and without Selenium."""
        enable_selenium(True)
        with_selenium_time = self.time_crawl(DYNAMIC_WEBSITES)
        logging.info(f"Time with Selenium: {with_selenium_time}")

        enable_selenium(False)
        without_selenium_time = self.time_crawl(DYNAMIC_WEBSITES)
        logging.info(f"Time without Selenium: {without_selenium_time}")

        # Add a tolerance to account for small timing variations
        self.assertGreater(
            with_selenium_time + 0.1,
            without_selenium_time,
            "Selenium should take more time than no Selenium"
        )


if __name__ == "__main__":
    unittest.main()
