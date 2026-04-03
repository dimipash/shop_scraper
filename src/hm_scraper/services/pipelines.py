import json
from pathlib import Path
from typing import Any

import structlog
from scrapy import Spider

from hm_scraper.config import settings
from hm_scraper.models import Product

logger = structlog.get_logger(__name__)


class JsonExportPipeline:
    """
    Pipeline responsible for serializing validated Product data into a JSON file.
    Expects items to be instances of the strictly typed Product Pydantic model.
    """

    def __init__(self) -> None:
        self.file_path = Path(settings.output_file)
        # Ensure the directory exists in case config points to a sub-folder
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def process_item(self, item: Any, spider: Spider) -> Any:
        if not isinstance(item, Product):
            logger.warning(
                "Dropped item: Not a valid Product model", item_type=str(type(item))
            )
            return item

        # Use Pydantic V2 native serialization
        data = item.model_dump()

        # Writing as a single JSON object as requested by the task
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        logger.info(
            "product_exported_successfully",
            product_name=item.name,
            file_path=str(self.file_path),
        )

        return item
