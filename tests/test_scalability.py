import unittest
import requests
from multiprocessing.pool import ThreadPool
import time

class TestScalability(unittest.TestCase):
    def test_small_dataset(self):
        response = requests.post("http://localhost:5000/start-crawl", json={"dataset_size": 10})
        self.assertEqual(response.status_code, 200, "Failed to start crawl for small dataset")

    def test_large_dataset(self):
        response = requests.post("http://localhost:5000/start-crawl", json={"dataset_size": 1000})
        self.assertEqual(response.status_code, 200, "Failed to start crawl for large dataset")

    def test_concurrent_requests(self):
        url = "http://localhost:5000/start-crawl"
        data = [{"dataset_size": i} for i in range(10, 50, 10)]

        def make_request(payload):
            retries = 3
            for _ in range(retries):
                response = requests.post(url, json=payload)
                print(f"Request with {payload} returned {response.status_code}")
                if response.status_code == 200:
                    return response.status_code
                time.sleep(1)
            return response.status_code

        pool = ThreadPool(5)
        statuses = pool.map(make_request, data)
        print(f"Statuses: {statuses}")
        self.assertTrue(all(status == 200 for status in statuses), "Some requests failed")


if __name__ == "__main__":
    unittest.main()
