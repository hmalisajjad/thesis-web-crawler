import unittest
from scrapy.http import Request
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider

class TestRobustness(unittest.TestCase):
    def setUp(self):
        self.spider = MultiFrameworkSpider()

    def test_malformed_url(self):
        malformed_url = "htp://malformed_url"
        request = Request(url=malformed_url)
        try:
            response = self.spider.parse(request)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

if __name__ == "__main__":
    unittest.main()