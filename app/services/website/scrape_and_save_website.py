import asyncio
from app.crud.crud_user import crud_user
from app.db.async_session import AsyncSessionLocal
from app.models import User
from app.services.website.service import WebsiteService
from app.services.crawler.crawler_service import run_crawler_service
from app.core.logger import logger
from app.utils.deduplication import deduplicate_markdown_lines
from app.utils.split_chunks import split_to_chunks
from app.utils.validation import check_website
from app.vectorstore.embed_chunk import embed_chunk


async def scrape_and_store_website(url: str, user_id: int):

    async with AsyncSessionLocal() as db:
        user = await crud_user.get_single(db=db, criteria=User.id == user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        try:
            website_service = WebsiteService(db=db, user_id=user.id)
            await check_website(url=url, db=db, user_id=user_id)
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

            unique_chunks = list(dict.fromkeys(chunks_list))  # Removes duplicates #
            logger.info("Done!")

            logger.info("Storing embeddings...")
            await embed_chunk(chunks=unique_chunks, website=website, db=db)
            logger.info("Done!")
            return {"id": str(website.id), "url": website.url, "title": website.title}

        except Exception as e:
            logger.error(f"[ERROR] {e}")
            raise
