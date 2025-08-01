import asyncio
from pydantic import HttpUrl
from app.api.deps import db_dependency, user_dependency
from app.services.embedding.service import EmbeddingService
from app.services.website.service import WebsiteService
from app.services.crawler.crawler_service import run_crawler_service
from app.core.logger import logger
from app.utils.deduplication import deduplicate_markdown_lines
from app.utils.split_chunks import split_to_chunks
from app.utils.validation import check_website


async def scrape_and_store_website(url: HttpUrl, user: user_dependency, db: db_dependency):
    try:
        website_service = WebsiteService(db=db, user=user)
        embedding_service = EmbeddingService(website_url=str(url), db=db)

        await check_website(url=str(url), db=db)
        logger.info(f"Scraping website: {url}")
        title, markdown_list = await run_crawler_service(url=url)

        logger.info("Removing duplicates...")
        markdown_list = await asyncio.to_thread(deduplicate_markdown_lines, markdown_list)
        logger.info("Done!")

        logger.info("Saving website to database...")
        website = await website_service.create_website(title=title, url=url)
        logger.info("Done!")

        chunks_list = []
        logger.info("Splitting markdown into chunks...")
        for markdown in markdown_list:
            chunks = await asyncio.to_thread(split_to_chunks, markdown)
            chunks_list.extend(chunks)

        unique_chunks = list(dict.fromkeys(chunks_list)) # Removes duplicates #
        logger.info("Done!")

        logger.info("Storing embeddings...")
        await embedding_service.create_embeddings(chunks=unique_chunks)
        logger.info("Done!")

    except Exception as e:
        logger.error(f"[ERROR] {e}")
        raise

    return website