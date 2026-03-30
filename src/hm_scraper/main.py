import structlog
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from hm_scraper.spiders.hm_spider import HMProductSpider

# Setup structured logging
logger = structlog.get_logger()


def run_scraper() -> None:
    settings = get_project_settings()

    # Configure the pipeline and output settings programmatically
    settings.setdict(
        {
            "ITEM_PIPELINES": {
                "hm_scraper.services.pipelines.JsonExportPipeline": 300,
            },
            "LOG_LEVEL": "INFO",
        }
    )

    process = CrawlerProcess(settings)
    logger.info("Starting H&M scraper process")

    process.crawl(HMProductSpider)
    process.start()  # The script will block here until the crawling is finished


if __name__ == "__main__":
    run_scraper()
