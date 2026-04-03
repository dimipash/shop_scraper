import json
import re
from typing import Any, Generator

import scrapy
from scrapy.http import Response

from hm_scraper.models import Product
from hm_scraper.services.parser import parse_hm_product_html


class HMProductSpider(scrapy.Spider):
    name = "hm_product"
    start_urls = [
        "https://webcache.googleusercontent.com/search?q=cache:https://www2.hm.com/bg_bg/productpage.1274171042.html"
    ]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        },
        # Senior tip: Add a small delay to look less like a bot
        "DOWNLOAD_DELAY": 1.5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def parse(self, response: Response) -> Generator[Product, None, None]:
        html_content = response.text
        
        product = parse_hm_product_html(html_content, current_url=response.url)
        
        if product:
            yield product
        else:
            self.logger.error("Failed to parse product data from HTML")
