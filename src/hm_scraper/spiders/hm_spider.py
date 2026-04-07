from typing import Generator

import scrapy
import structlog
from scrapy.http import HtmlResponse, Response

from hm_scraper.config import settings
from hm_scraper.models import Product
from hm_scraper.services.parser import parse_product

logger = structlog.get_logger(__name__)


class HMProductSpider(scrapy.Spider):
    """
    Spider responsible strictly for HTTP orchestration.
    It configures aggressive headers to bypass WAF / bot protection
    and delegates all HTML parsing to `services.parser`.
    """

    name = "hm_product"
    start_urls = [settings.target_url]

    # Implementing "Attempt 2" from Context: Mobile impersonation
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,bg;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Cache-Control": "max-age=0",
        },
        "DOWNLOAD_DELAY": 2.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        # Allow 403s through to our parse method instead of infinite Scrapy retries
        "HTTPERROR_ALLOW_ALL": True,
    }

    def parse(self, response: Response) -> Generator[Product, None, None]:
        if response.status != 200:
            logger.error("http_request_rejected", status=response.status, url=response.url)
            return

        if not isinstance(response, HtmlResponse):
            logger.error("unexpected_response_type", type=str(type(response)))
            return

        logger.info("page_fetched_successfully", url=response.url)

        try:
            # Delegate parsing to our pure, testable function
            product = parse_product(response)
            yield product
        except Exception as e:
            logger.exception("parsing_fatal_error", error=str(e), url=response.url)
