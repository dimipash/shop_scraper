import json
from pathlib import Path
from typing import Any

from itemadapter import ItemAdapter
from scrapy import Spider

from hm_scraper.models import Product


class JsonExportPipeline:
    def __init__(self) -> None:
        self.file_path = Path("output.json")

    def process_item(self, item: Product, spider: Spider) -> dict[str, Any]:
        # Convert the Pydantic model to a dict for JSON serialization
        data = ItemAdapter(item).asdict()

        # Writing as a single JSON object as per the task example [cite: 13, 14]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        spider.logger.info(f"Successfully saved product data to {self.file_path}")
        return data
