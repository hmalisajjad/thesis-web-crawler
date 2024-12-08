import unittest
import requests

BASE_URL = "http://localhost:5000"

class TestAPI(unittest.TestCase):
    def test_start_crawl(self):
        payload = {"dataset_size": 10}
        response = requests.post(f"{BASE_URL}/start-crawl", json=payload)  
        self.assertEqual(response.status_code, 200)

    def test_get_results(self):
        response = requests.get(f"{BASE_URL}/results")
        self.assertIn(response.status_code, [200, 404])

    def test_crawl_status(self):
        response = requests.get(f"{BASE_URL}/crawl-status")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()