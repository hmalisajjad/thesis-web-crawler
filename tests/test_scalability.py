from locust import HttpUser, task 

class CrawlerUser(HttpUser):
    host = "http://localhost:5000"  # Set your API host here

    @task
    def start_crawl(self):
        self.client.post("/start-crawl")