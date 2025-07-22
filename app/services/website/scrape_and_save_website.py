from app.api.deps import db_dependency, user_dependency
from app.services.website.service import WebsiteService
from app.services.crawler.crawler_service import run_crawler_service
from app.utils.db_transaction import db_transactional_async
from app.core.logger import logger
from app.vectorstore.store_embeddings import store_embedding_data

@db_transactional_async
async def scrape_and_store_website(url: str, user: user_dependency, db: db_dependency):
    website_service = WebsiteService(db=db, user=user)
    logger.info(f"Scraping website: {url}")
    title, full_markdown = await run_crawler_service(url=url)
    logger.info("Done!")

    logger.info("Saving website to database...")
    await website_service.create_website(title=title, url=url, markdown=full_markdown)
    logger.info("Done!")

    logger.info("Storing embeddings...")
    await store_embedding_data(db=db, user_id=user.id)

    return f"Website stored successfully. Title: {title}, URL: {url}"