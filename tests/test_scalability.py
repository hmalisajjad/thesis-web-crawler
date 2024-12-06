from locust import HttpUser, task, between

class CrawlerUser(HttpUser):
    host = "http://localhost:5000"
    wait_time = between(1, 5)

    @task(1)
    def small_dataset_crawl(self):
        response = self.client.post("/start-crawl", json={"dataset_size": 10})
        if response.status_code == 200:
            print(f"Small dataset crawl started successfully: {response.json()}")
        else:
            print(f"Error during small dataset crawl: {response.status_code} - {response.text}")
