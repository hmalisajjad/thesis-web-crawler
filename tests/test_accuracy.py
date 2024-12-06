import unittest
from scrapy.http import HtmlResponse
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider, normalize_url

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
        <script>console.log('Custom chatbot script running');</script>
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

        expected_chatbot_url = normalize_url("https://example.com/chatbot-widget")
        detected_chatbots = [normalize_url(chatbot_url) for chatbot_url in detected_chatbots]

        self.assertIn(expected_chatbot_url, detected_chatbots, f"Expected iframe URL not found in detected chatbots: {detected_chatbots}")

    def test_custom_chatbot_detection(self):
        html = '''
        <html><head></head><body>
        <div id="custom-chatbot">Custom chatbot implementation</div>
        <script>console.log('Custom chatbot script running');</script>
        </body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        results = list(self.spider.parse(response))

        detected_chatbots = []
        for result in results:
            if isinstance(result, dict) and "detected_chatbots" in result:
                detected_chatbots = result.get("detected_chatbots", [])

        expected_custom_chatbot_url = normalize_url("http://example.com")
        detected_chatbots = [normalize_url(chatbot_url) for chatbot_url in detected_chatbots]

        self.assertIn(expected_custom_chatbot_url, detected_chatbots, f"Custom chatbot not detected in detected chatbots: {detected_chatbots}")

    def test_metadata_extraction(self):
        html = '''
        <html><head><title>Test Page</title></head>
        <body><p>Chat with our virtual assistant powered by OpenAI</p>
        <iframe src="https://example.com/chatbot-widget"></iframe>
        <script>console.log('Metadata extraction test');</script>
        </body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        results = list(self.spider.parse(response))

        extracted_metadata = []
        for result in results:
            if isinstance(result, dict):
                extracted_metadata.append(result)

        # Check that metadata extraction includes expected fields
        for metadata in extracted_metadata:
            self.assertIn("main_url", metadata, "Main URL missing from metadata.")
            self.assertIn("title", metadata, "Title missing from metadata.")
            self.assertIn("date_collected", metadata, "Date collected missing from metadata.")

    def test_large_dataset_accuracy(self):
        # Simulating a large dataset of 100 websites
        urls = [f"http://example{i}.com" for i in range(100)]
        for url in urls:
            # Update page_source with new HTML content for each URL iteration
            html = f'''
            <html><head><title>Test Page {url}</title></head>
            <body><p>Chatbot reference for testing at {url}</p>
            <iframe src="{url}/chatbot-widget"></iframe>
            </body></html>
            '''
            self.spider.driver.page_source = html  # Update the mocked page_source here

            response = HtmlResponse(url=url, body=html, encoding='utf-8')
            results = list(self.spider.parse(response))

            detected_chatbots = []
            for result in results:
                if isinstance(result, dict) and "detected_chatbots" in result:
                    detected_chatbots = result.get("detected_chatbots", [])

            # Debug print to see what's being detected for each URL
            print(f"Detected chatbots for {url}: {detected_chatbots}")

            # Normalizing URL to match the way it's detected in the spider
            expected_chatbot_url = normalize_url(f"{url}/chatbot-widget")
            detected_chatbots = [normalize_url(chatbot_url) for chatbot_url in detected_chatbots]

            self.assertIn(expected_chatbot_url, detected_chatbots,
                          f"Expected iframe URL not found in detected chatbots for {url}: {detected_chatbots}")

if __name__ == "__main__":
    unittest.main()
