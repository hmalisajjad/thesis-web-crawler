import unittest
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import run_crawler_in_thread  

class TestEfficiency(unittest.TestCase):
    def test_crawl_time(self):
        start_time = time.time()
        run_crawler_in_thread()
        end_time = time.time()
        duration = end_time - start_time
        self.assertLess(duration, 60, "Crawl took too long")

if __name__ == "__main__":
    unittest.main()