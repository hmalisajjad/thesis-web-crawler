import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from db.database import load_from_json

class TestMetadata(unittest.TestCase):
    def test_metadata_completeness(self):
        # Adjust the path to point to the correct location
        path = os.path.abspath("../backend/chatbot_data.json")
        print(f"Loading data from: {path}")
        data = load_from_json(path)
        assert data is not None, f"Failed to load data from {path}"

        for item in data:
            self.assertIn("main_url", item, "Missing 'main_url' in metadata")
            self.assertIn("title", item, "Missing 'title' in metadata")
            self.assertIn("detected_chatbots", item, "Missing 'detected_chatbots' in metadata")
            self.assertIn("keywords_detected", item, "Missing 'keywords_detected' in metadata")
            self.assertIn("date_collected", item, "Missing 'date_collected' in metadata")

    def test_metadata_accuracy(self):
        ground_truth = {
            "https://example.com": {
                "title": "Example Domain",
                "detected_chatbots": ["example-bot"],
                "keywords_detected": ["chatbot"],
                "date_collected": "2024-12-07"
            }
        }

        path = os.path.abspath("../backend/chatbot_data.json")
        data = load_from_json(path)
        assert data is not None, f"Failed to load data from {path}"

        for item in data:
            url = item.get("main_url")
            if url in ground_truth:
                truth = ground_truth[url]
                self.assertEqual(item["title"], truth["title"], f"Title mismatch for {url}")
                self.assertListEqual(item["detected_chatbots"], truth["detected_chatbots"], f"Chatbots mismatch for {url}")
                self.assertListEqual(item["keywords_detected"], truth["keywords_detected"], f"Keywords mismatch for {url}")

    def test_missing_metadata(self):
        path = os.path.abspath("../backend/chatbot_data.json")
        data = load_from_json(path)
        assert data is not None, f"Failed to load data from {path}"

        missing_titles = [item["main_url"] for item in data if not item.get("title")]
        missing_chatbots = [item["main_url"] for item in data if not item.get("detected_chatbots")]

        self.assertLess(len(missing_titles), len(data) * 0.05, "Too many missing titles")
        self.assertLess(len(missing_chatbots), len(data) * 0.05, "Too many missing detected chatbots")

if __name__ == "__main__":
    unittest.main()
