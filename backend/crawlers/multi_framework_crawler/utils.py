import random
from scrapy import signals
from scrapy.exceptions import NotConfigured
import logging

def get_proxies():
    # Replace with your actual proxy list or integrate with a proxy provider API
    return [
        'http://proxy1.example.com:8000',
        'http://proxy2.example.com:8031',
        'http://proxy3.example.com:8032',
        # Add more proxies as needed
    ]

class ProxyMiddleware:
    def __init__(self, proxies):
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler):
        proxies = get_proxies()
        if not proxies:
            raise NotConfigured
        return cls(proxies)

    def process_request(self, request, spider):
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy

    def process_exception(self, request, exception, spider):
        logging.error(f"Proxy failed: {request.meta.get('proxy')}, exception: {exception}")
        # Optionally remove the failed proxy from the pool
        if 'proxy' in request.meta:
            self.proxies.remove(request.meta['proxy'])