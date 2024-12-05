import unittest
from scrapy.http import HtmlResponse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider

class TestAccuracy(unittest.TestCase):
    def setUp(self):
        self.spider = MultiFrameworkSpider()

    def test_keyword_detection(self):
        html = '''
        <html><head><title>Test Page</title></head>
        <body><p>Chat with our virtual assistant powered by OpenAI</p></body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        result = next(self.spider.parse(response))

        self.assertIn("OpenAI", result["keywords_detected"])
        self.assertIn("virtual assistant", result["keywords_detected"])

    def test_chatbot_detection(self):
        html = '''
        <html><head></head><body>
        <iframe src="https://example.com/chatbot-widget"></iframe>
        </body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        result = next(self.spider.parse(response))

        self.assertIn("https://example.com/chatbot-widget", result["detected_chatbots"])

if __name__ == "__main__":
    unittest.main()
