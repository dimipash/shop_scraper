import re

import structlog
from scrapy.http import HtmlResponse

from hm_scraper.models import Product

logger = structlog.get_logger(__name__)


def parse_product(response: HtmlResponse) -> Product:
    """
    Extracts product data from the H&M product page HTML.
    Isolating this logic allows us to unit test the extraction independently
    of the Scrapy Spider / Network.
    """
    logger.info("parsing_html", url=response.url)

    # Name Extraction
    name = response.css(
        "h1.product-item-headline::text, h1.ProductTitle-module--productTitle__6hJ_V::text"
    ).get(default="")
    name = name.strip() if name else "Unknown"

    # Price Extraction (handling Bulgarian currency formatting e.g., "29,99 лв.")
    price_str = response.css(
        ".product-item-price span::text, .Price-module--price__1tGzi::text"
    ).get(default="0")
    clean_price = re.sub(r"[^\d.]", "", price_str.replace(",", "."))
    price = float(clean_price) if clean_price else 0.0

    # Current Color Extraction
    current_color = response.css(
        ".product-colors .active::text, .product-colors .product-item-selection::text"
    ).get(default="")
    current_color = current_color.strip() if current_color else "Default"

    # Available Colors Extraction
    available_colors_elements = response.css(".filter-option.image::attr(alt)").getall()
    available_colors = [c.strip() for c in available_colors_elements if c.strip()]
    if not available_colors:
        available_colors = [current_color]

    # Reviews Handling
    reviews_count_str = response.css("button.review-count::text").get(default="0")
    clean_rev_count = re.sub(r"\D", "", reviews_count_str)
    reviews_count = int(clean_rev_count) if clean_rev_count else 0

    reviews_score_str = response.css("div.stars::attr(data-rating)").get(default="0")
    clean_score = re.sub(r"[^\d.]", "", reviews_score_str.replace(",", "."))
    reviews_score = float(clean_score) if clean_score else 0.0

    # Validate against our Pydantic data contract
    return Product(
        name=name,
        price=price,
        current_color=current_color,
        available_colors=available_colors,
        reviews_count=reviews_count,
        reviews_score=reviews_score,
    )
