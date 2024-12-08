import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from scrapy.http import HtmlResponse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider

class TestFlexibility(unittest.TestCase):
    @patch("crawlers.multi_framework_crawler.multi_framework_spider.webdriver.Chrome")
    def test_iframe_detection(self, mock_driver):
        spider = MultiFrameworkSpider(keywords=["iframe-chatbot"])

        # Mock Selenium driver
        mock_driver_instance = mock_driver.return_value
        mock_driver_instance.page_source = (
            '<html><body><iframe src="https://chatbot.example.com"></iframe></body></html>'
        )

        # Mock the Scrapy response
        url = "https://example.com"
        body = b'<html><head><title>Test Page</title></head><body></body></html>'
        mock_response = HtmlResponse(url=url, body=body, encoding='utf-8')

        # Patch the spider's driver
        with patch.object(spider, 'driver', mock_driver_instance):
            results = list(spider.parse(mock_response))

        # Filter out intermediate Request objects
        parsed_results = [result for result in results if isinstance(result, dict)]

        # Ensure the result is not empty
        self.assertTrue(parsed_results, "No dictionary results returned from parse method")
        # Validate the detected chatbots
        self.assertIn("https://chatbot.example.com", parsed_results[0]["detected_chatbots"])


    @patch("crawlers.multi_framework_crawler.multi_framework_spider.webdriver.Chrome")
    def test_unconventional_structure(self, mock_driver):
        spider = MultiFrameworkSpider(keywords=["custom-chatbot"])

        # Mock Selenium driver
        mock_driver_instance = mock_driver.return_value
        mock_driver_instance.page_source = (
            '<html><body><div class="chat-widget" data-api="custom-api"></div></body></html>'
        )

        # Mock the Scrapy response
        url = "https://example.com"
        body = b'<html><head><title>Test Page</title></head><body></body></html>'
        mock_response = HtmlResponse(url=url, body=body, encoding='utf-8')

        # Patch the spider's driver
        with patch.object(spider, 'driver', mock_driver_instance):
            results = list(spider.parse(mock_response))

        # Validate the detected unconventional structure
        self.assertTrue(results, "No results returned from parse method")
        self.assertIn("custom-api", results[0]["detected_chatbots"])


if __name__ == "__main__":
    unittest.main()
