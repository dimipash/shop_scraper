from scrapy.http import HtmlResponse, Request

from hm_scraper.models import Product
from hm_scraper.services.parser import parse_product


def test_parse_product_with_mock_html() -> None:
    """
    Because we isolated the parser from the spider, we can test DOM extraction
    logic synchronously with fake HTML, entirely bypassing the network.
    """
    # Arrange (Mock the DOM)
    html_content = b"""
    <html>
        <body>
            <h1 class="product-item-headline">Cool Denim Jacket</h1>
            <div class="product-item-price"><span>129,99 лв.</span></div>
            <div class="product-colors">
                <span class="active">Blue</span>
                <img class="filter-option image" alt="Red"/>
            </div>
            <button class="review-count">24 reviews</button>
            <div class="stars" data-rating="4.8"></div>
        </body>
    </html>
    """
    request = Request(url="https://mock.com/product/123")
    response = HtmlResponse(
        url=request.url, request=request, body=html_content, encoding="utf-8"
    )

    # Act
    product = parse_product(response)

    # Assert (Ensure Regex logic and type casting worked)
    assert isinstance(product, Product)
    assert product.name == "Cool Denim Jacket"
    assert product.price == 129.99
    assert product.current_color == "Blue"
    assert "Red" in product.available_colors
    assert product.reviews_count == 24
    assert product.reviews_score == 4.8
