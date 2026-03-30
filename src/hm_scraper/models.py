from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str
    price: float
    current_color: str
    available_colors: list[str]
    reviews_count: int
    reviews_score: float

    class Config:
        frozen = True
