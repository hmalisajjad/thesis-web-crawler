import unittest
from db.database import load_from_json

class TestMetadata(unittest.TestCase):
    def test_metadata_completeness(self):
        data = load_from_json("backend/chatbot_data.json")
        for item in data:
            self.assertIn("main_url", item)
            self.assertIn("title", item)
            self.assertIn("detected_chatbots", item)
            self.assertIn("keywords_detected", item)
            self.assertIn("date_collected", item)

if __name__ == "__main__":
    unittest.main()