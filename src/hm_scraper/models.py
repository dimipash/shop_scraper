from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    """Data contract representing the scraped H&M product."""

    name: str = Field(..., description="The name of the product")
    price: float = Field(..., description="Price of the product as a double")
    current_color: str = Field(..., description="Currently selected default color")
    available_colors: list[str] = Field(..., description="List of all available colors")
    reviews_count: int = Field(..., description="Total number of reviews")
    reviews_score: float = Field(..., description="Review score (e.g., out of 5.0)")

    # Pydantic V2 config syntax
    model_config = ConfigDict(frozen=True)
