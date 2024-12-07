import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from scrapy.http import HtmlResponse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider

class TestFlexibility(unittest.TestCase):
    @patch("crawlers.multi_framework_crawler.multi_framework_spider.BeautifulSoup")
    def test_custom_keywords(self, mock_soup):
        spider = MultiFrameworkSpider(keywords=["chat", "chatbot"])
        self.assertIn("chat", spider.keywords)
        self.assertIn("chatbot", spider.keywords)

    def test_dynamic_urls(self):
        spider = MultiFrameworkSpider(urls=["https://test1.com", "https://test2.com"])
        self.assertIn("https://test1.com", spider.start_urls)
        self.assertIn("https://test2.com", spider.start_urls)

    @patch("crawlers.multi_framework_crawler.multi_framework_spider.webdriver.Chrome")
    def test_iframe_detection(self, mock_driver):
        spider = MultiFrameworkSpider(keywords=["iframe-chatbot"])

        # Mock Selenium driver
        mock_driver_instance = mock_driver.return_value
        mock_driver_instance.page_source = (
            '<html><body><iframe src="https://chatbot.example.com"></iframe></body></html>'
        )

        # Create a mock Scrapy response
        url = "https://example.com"
        body = b'<html><head><title>Test Page</title></head><body></body></html>'
        mock_response = HtmlResponse(url=url, body=body, encoding='utf-8')

        # Call the parse method
        with patch.object(spider, 'driver', mock_driver_instance):  # Mock the driver in the spider
            results = [result for result in spider.parse(mock_response) if isinstance(result, dict)]

        # Validate the detected chatbots
        self.assertIn("https://chatbot.example.com", results[0]["detected_chatbots"])

    @patch("crawlers.multi_framework_crawler.multi_framework_spider.webdriver.Chrome")
    def test_unconventional_structure(self, mock_driver):
        spider = MultiFrameworkSpider(keywords=["custom-chatbot"])

        # Mock Selenium driver
        mock_driver_instance = mock_driver.return_value
        mock_driver_instance.page_source = (
            '<html><body><div class="chat-widget" data-api="custom-api"></div></body></html>'
        )

        # Create a mock Scrapy response
        url = "https://example.com"
        body = b'<html><head><title>Test Page</title></head><body></body></html>'
        mock_response = HtmlResponse(url=url, body=body, encoding='utf-8')

        # Call the parse method
        with patch.object(spider, 'driver', mock_driver_instance):  # Mock the driver in the spider
            results = [result for result in spider.parse(mock_response) if isinstance(result, dict)]

        # Validate the detected unconventional structure
        self.assertIn("custom-api", results[0]["detected_chatbots"])


if __name__ == "__main__":
    unittest.main()
