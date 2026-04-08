import structlog
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from hm_scraper.spiders.hm_spider import HMProductSpider

logger = structlog.get_logger(__name__)


def run_scraper() -> None:
    """
    Main entrypoint to bootstrap the Scrapy engine programmatically.
    This avoids the need for raw 'scrapy crawl' CLI commands, making
    it significantly easier to execute via a standard python module runtime.
    """
    settings = get_project_settings()

    # Programmatic configuration: we dynamically inject our pipeline here
    # Instead of relying on a global settings.py scaffolding.
    settings.setdict(
        {
            "ITEM_PIPELINES": {
                "hm_scraper.services.pipelines.JsonExportPipeline": 300,
            },
            # Keeping native Scrapy logs to WARNING means our explicit
            # Structlog INFO calls are highly visible and un-polluted.
            "LOG_LEVEL": "WARNING",
        }
    )

    process = CrawlerProcess(settings)

    logger.info("system_startup", message="Initializing H&M Product Scraper Engine")

    process.crawl(HMProductSpider)
    process.start()

    logger.info("system_shutdown", message="Scraping process complete")


if __name__ == "__main__":
    run_scraper()
