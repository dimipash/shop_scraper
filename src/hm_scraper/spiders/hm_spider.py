import json
import re
from typing import Any, Generator

import scrapy
from scrapy.http import Response

from hm_scraper.models import Product


class HMProductSpider(scrapy.Spider):
    name = "hm_product"
    start_urls = ["https://www2.hm.com/bg_bg/productpage.1274171042.html"]

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
        script_text = response.xpath(
            "//script[contains(text(), 'productArticleDetails')]/text()"
        ).get()

        if not script_text:
            self.logger.error("Required product data script not found in HTML")
            return

        json_match = re.search(r"var productArticleDetails = (\{.*?\});", script_text)
        if not json_match:
            self.logger.error("Failed to extract product JSON from script text")
            return

        raw_data = json.loads(json_match.group(1))

        # The specific article ID from the URL
        article_id = "1274171042"
        article_info = raw_data.get(article_id, {})

        raw_price = str(article_info.get("whitePriceValue", "0")).replace(",", ".")
        price = float(re.sub(r"[^\d.]", "", raw_price))

        reviews_count = int(
            response.css("span.reviews-number::text").re_first(r"\d+") or 0
        )
        reviews_score = float(
            response.css("span.reviews-rating::text").re_first(r"[\d.]+") or 0.0
        )

        available_colors = [
            variant.get("name")
            for variant in raw_data.values()
            if isinstance(variant, dict) and "name" in variant
        ]

        yield Product(
            name=response.css("h1.primary-product-name::text").get(default="").strip(),
            price=price,
            current_color=article_info.get("name", "Unknown"),
            available_colors=available_colors,
            reviews_count=reviews_count,
            reviews_score=reviews_score,
        )
