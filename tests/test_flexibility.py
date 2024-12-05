import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider

class TestFlexibility(unittest.TestCase):
    def test_custom_keywords(self):
        spider = MultiFrameworkSpider(keywords=["chat", "chatbot"])
        self.assertIn("chat", spider.keywords)
        self.assertIn("chatbot", spider.keywords)

    def test_dynamic_urls(self):
        spider = MultiFrameworkSpider(urls=["https://test1.com", "https://test2.com"])
        self.assertIn("https://test1.com", spider.start_urls)
        self.assertIn("https://test2.com", spider.start_urls)

if __name__ == "__main__":
    unittest.main()