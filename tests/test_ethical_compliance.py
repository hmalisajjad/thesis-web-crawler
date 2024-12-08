import json
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from crawlers.multi_framework_crawler.settings import ROBOTSTXT_OBEY, DOWNLOAD_DELAY

class TestEthicalCompliance(unittest.TestCase):
    def test_robots_txt_compliance(self):
        self.assertTrue(ROBOTSTXT_OBEY, "Crawler is not configured to obey robots.txt")

    def test_download_delay(self):
        self.assertGreaterEqual(DOWNLOAD_DELAY, 1, "Download delay is too short")

    def test_no_personal_data_storage(self):
        sensitive_fields = ["email", "phone", "address"]
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/chatbot_data.json'))
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        for item in data:
            for field in sensitive_fields:
                self.assertNotIn(field, item)

if __name__ == "__main__":
    unittest.main()