import unittest
from parameterized import parameterized
from scrapy.http import HtmlResponse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider


class TestMultiFrameworkSpider(unittest.TestCase):
    def setUp(self):
        # Initialize the MultiFrameworkSpider instance
        self.spider = MultiFrameworkSpider()

    @parameterized.expand([
        ("simple_keywords", '''
        <html><head><title>Test Page</title></head>
        <body><p>Chat with ChatGPT, a virtual assistant!</p></body></html>''',
         {"keywords_detected": ["ChatGPT", "chat", "virtual assistant"], "detected_chatbots": []}),

        ("iframe_widget", '''
        <html><head></head><body>
        <iframe src="https://example.com/chatbot-widget"></iframe>
        </body></html>''',
         {"keywords_detected": [], "detected_chatbots": ["https://example.com/chatbot-widget"]}),

        ("no_keywords_iframe", '''
        <html><head><title>No Keywords</title></head>
        <body><p>No relevant content here</p></body></html>''',
         {"keywords_detected": [], "detected_chatbots": []}),

        ("multiple_iframes", '''
        <html><head></head><body>
        <iframe src="https://example.com/chatbot-widget"></iframe>
        <iframe src="https://other.com/live-chat"></iframe>
        </body></html>''',
         {"keywords_detected": [], "detected_chatbots": ["https://example.com/chatbot-widget", "https://other.com/live-chat"]}),
    ])
    def test_parsing(self, name, html_body, expected):
        """
        Test the spider's ability to parse keywords and detect chatbots in HTML content.
        """
        # Create a mock HTML response
        response = HtmlResponse(url='http://example.com', body=html_body, encoding='utf-8')

        # Run the spider's parse method
        result = next(self.spider.parse(response))

        # Assert detected keywords
        for keyword in expected["keywords_detected"]:
            self.assertIn(keyword, result["keywords_detected"], f"Keyword '{keyword}' not detected as expected.")

        # Assert detected chatbot iframe URLs
        for iframe_url in expected["detected_chatbots"]:
            self.assertIn(iframe_url, result["detected_chatbots"], f"Iframe URL '{iframe_url}' not detected as expected.")

    def test_missing_title(self):
        """
        Test the spider's behavior when the HTML page has no title tag.
        """
        html = '<html><head></head><body><p>No title here!</p></body></html>'
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        result = next(self.spider.parse(response))

        # Assert the fallback title value
        self.assertEqual(result["title"], "No Title", "Title fallback did not work as expected.")

    def test_empty_response(self):
        """
        Test the spider's behavior when the response body is empty.
        """
        html = ''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        with self.assertRaises(StopIteration):
            next(self.spider.parse(response))

    def test_keyword_case_insensitivity(self):
        """
        Test that keywords are detected regardless of their case in the HTML content.
        """
        html = '''
        <html><head></head><body><p>CHAT with our virtual Assistant powered by openAI</p></body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        result = next(self.spider.parse(response))

        # Assert case-insensitive keyword detection
        self.assertIn("chat", result["keywords_detected"])
        self.assertIn("virtual assistant", result["keywords_detected"])
        self.assertIn("OpenAI", result["keywords_detected"])

    def test_invalid_iframe_src(self):
        """
        Test that invalid iframe `src` attributes (e.g., `javascript:void(0)`) are ignored.
        """
        html = '''
        <html><head></head><body>
        <iframe src="javascript:void(0)"></iframe>
        <iframe src="https://example.com/chatbot-widget"></iframe>
        </body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        result = next(self.spider.parse(response))

        # Assert only valid iframe src is detected
        self.assertNotIn("javascript:void(0)", result["detected_chatbots"])
        self.assertIn("https://example.com/chatbot-widget", result["detected_chatbots"])

    def test_dynamic_iframe_parsing(self):
        """
        Test that dynamically loaded iframe URLs (e.g., through JavaScript) are not detected (as WebDriver is used).
        """
        html = '''
        <html><head></head><body>
        <script>document.write('<iframe src="https://example.com/dynamic-widget"></iframe>');</script>
        </body></html>
        '''
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        result = next(self.spider.parse(response))

        # Assert that dynamically added iframes are not detected (since this is static parsing)
        self.assertNotIn("https://example.com/dynamic-widget", result["detected_chatbots"])


if __name__ == "__main__":
    unittest.main()
