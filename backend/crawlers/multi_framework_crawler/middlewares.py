import os

class ScraperAPIMiddleware:
    def process_request(self, request, spider):
        scraperapi_key = os.getenv('SCRAPERAPI_KEY', '8ffff6c087fde36ed0a1c2c5cca007723')
        request.meta['proxy'] = f"http://scraperapi:{scraperapi_key}@proxy-server.scraperapi.com:8001"
