import logging
import os

import psycopg

from tomorrow.client import TomorrowClient
from tomorrow.database import PostgresWeatherDB, get_postgres_kwargs
from tomorrow.scraper import TomorrowScraper


def configure_logging() -> logging.Logger:
    """Configure logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    return logging.getLogger(__name__)


def main():
    """Run the Tomorrow.io scraper."""
    logger = configure_logging()
    logger.info("Running Tomorrow.io scraper...")

    tomorrow_api_key = os.getenv("TOMORROW_API_KEY")
    if not tomorrow_api_key:
        raise ValueError("TOMORROW_API_KEY environment variable is not set.")

    conn_kwargs = get_postgres_kwargs()
    with psycopg.connect(**conn_kwargs) as conn:
        postgres_db = PostgresWeatherDB(conn)
        tomorrow_client = TomorrowClient(api_key=tomorrow_api_key)
        tomorrow_scraper = TomorrowScraper(tomorrow_client, postgres_db)
        tomorrow_scraper.scrape()


if __name__ == "__main__":
    main()
