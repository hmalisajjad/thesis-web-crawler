import unittest
from scrapy.http import HtmlResponse
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider

class TestAccuracy(unittest.TestCase):
    def setUp(self):
        self.spider = MultiFrameworkSpider()
        # Mocking Selenium driver to avoid actual browser interaction
        self.spider.driver = MagicMock()
        
        # Mock the page_source or other driver interactions if used in `parse`
        self.spider.driver.page_source = '''
        <html><head><title>Test Page</title></head>
        <body><p>Chat with our virtual assistant powered by OpenAI</p>
        <iframe src="https://example.com/chatbot-widget"></iframe>
        </body></html>
        '''

        # Mock any method calls to driver if needed, like get(url)
        self.spider.driver.get = MagicMock()

    def test_keyword_detection(self):
        html = '''
        <html><head><title>Test Page</title></head>
        <body><p>Chat with our virtual assistant powered by OpenAI</p></body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        results = list(self.spider.parse(response))

        detected_keywords = []
        for result in results:
            if isinstance(result, dict) and "keywords_detected" in result:
                detected_keywords = [kw.lower() for kw in result.get("keywords_detected", [])]

        expected_keywords = ["openai", "virtual assistant"]

        for keyword in expected_keywords:
            self.assertIn(keyword, detected_keywords, f"Keyword '{keyword}' not detected in {detected_keywords}")

    def test_chatbot_detection(self):
        html = '''
        <html><head></head><body>
        <iframe src="https://example.com/chatbot-widget"></iframe>
        </body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        results = list(self.spider.parse(response))

        detected_chatbots = []
        for result in results:
            if isinstance(result, dict) and "detected_chatbots" in result:
                detected_chatbots = result.get("detected_chatbots", [])

        self.assertIn("https://example.com/chatbot-widget", detected_chatbots, f"Expected iframe URL not found in detected chatbots: {detected_chatbots}")

if __name__ == "__main__":
    unittest.main()
