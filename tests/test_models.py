import pytest
from pydantic import ValidationError

from hm_scraper.models import Product


def test_product_model_validates_types_correctly() -> None:
    # Arrange & Act
    product = Product(
        name="T-shirt",
        price=19.99,
        current_color="Black",
        available_colors=["Black", "White"],
        reviews_count=150,
        reviews_score=4.5,
    )

    # Assert
    assert product.name == "T-shirt"
    assert isinstance(product.price, float)
    assert product.price == 19.99


def test_product_model_fails_loudly_on_missing_fields() -> None:
    # We expect Pydantic to fail fast if we are missing fields like `price`
    with pytest.raises(ValidationError):
        Product(
            name="Incomplete T-shirt",
            # missing price, colors, etc
        )
