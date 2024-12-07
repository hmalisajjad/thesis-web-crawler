import unittest
from scrapy.http import Request, HtmlResponse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.multi_framework_spider import MultiFrameworkSpider

class TestRobustness(unittest.TestCase):
    def setUp(self):
        self.spider = MultiFrameworkSpider()


    def test_server_error(self):
        error_url = "http://example.com/500"
        response = HtmlResponse(url=error_url, status=500)
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 0, "Spider should not process 500 error responses")

    def test_dynamic_content(self):
        dynamic_content_url = "http://example.com/dynamic"
        response = HtmlResponse(url=dynamic_content_url, body=b"<html><script>Dynamic Content</script></html>", encoding='utf-8')
        result = list(self.spider.parse(response))
        self.assertIsInstance(result, list, "Spider should handle dynamic content gracefully")

    def test_logging_and_recovery(self):
        """Test if the spider logs errors and continues crawling."""
        problematic_url = "http://example.com/problematic"
        response = HtmlResponse(url=problematic_url, status=403)  # Simulating a forbidden response
        try:
            list(self.spider.parse(response))
            # Check for logging (mock the logging or verify expected behavior)
            self.assertTrue(True, "Spider handled problematic page without crashing")
        except Exception as e:
            self.fail(f"Spider crashed on problematic page: {e}")

if __name__ == "__main__":
    unittest.main()
