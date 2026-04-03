import json
import re
from typing import Optional

from hm_scraper.models import Product


def parse_hm_product_html(html_text: str, current_url: str = "") -> Optional[Product]:
    """Parse product JSON data embedded in H&M's HTML source."""
    # Find the JSON data embedded in the script tag
    json_match = re.search(r"var productArticleDetails = (\{.*?\});", html_text)
    
    if not json_match:
        return None

    try:
        raw_data = json.loads(json_match.group(1))
    except json.JSONDecodeError:
        return None

    # Determine article ID. We can extract it from the URL or fallback
    article_id_match = re.search(r"productpage\.(\d+)\.html", current_url)
    article_id = article_id_match.group(1) if article_id_match else None
    
    # If not found in URL, pick the first one from raw_data
    if not article_id and raw_data:
        article_id = list(raw_data.keys())[0]
        
    article_info = raw_data.get(article_id, {}) if article_id else {}

    raw_price = str(article_info.get("whitePriceValue", "0")).replace(",", ".")
    price = float(re.sub(r"[^\d.]", "", raw_price) or "0.0")

    available_colors = [
        variant.get("name")
        for variant in raw_data.values()
        if isinstance(variant, dict) and "name" in variant
    ]

    # For reviews, since we are doing purely string-based functional parsing,
    # we can use simple regex to extract them without full CSS selectors
    reviews_count = 0
    count_match = re.search(r'<span[^>]*class="[^"]*reviews-number[^"]*"[^>]*>\s*(\d+)', html_text)
    if count_match:
        reviews_count = int(count_match.group(1))

    reviews_score = 0.0
    score_match = re.search(r'<span[^>]*class="[^"]*reviews-rating[^"]*"[^>]*>\s*([\d.]+)', html_text)
    if score_match:
        reviews_score = float(score_match.group(1))

    # Name is often inside `<h1 class="primary-product-name">...</h1>`
    name = "Unknown"
    name_match = re.search(r'<h1[^>]*class="[^"]*primary-product-name[^"]*"[^>]*>(.*?)</h1>', html_text, re.IGNORECASE | re.DOTALL)
    if name_match:
        name = name_match.group(1).strip()
    else:
        # Fallback to model name if h1 not found
        name = article_info.get("title", "Unknown")

    return Product(
        name=name,
        price=price,
        current_color=article_info.get("name", "Unknown"),
        available_colors=available_colors,
        reviews_count=reviews_count,
        reviews_score=reviews_score,
    )
