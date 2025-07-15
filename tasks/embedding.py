from app.db.sync_session import SessionLocal
from app.vectorstore.store_embeddings import store_embedding_data
from tasks.celery_app import celery_app
from app.core.logger import logger

@celery_app.task(name="store_embeddings_task")
def store_embeddings_task(user_id: int):
    logger.info(f"Starting embedding task for user {user_id}")
    db = SessionLocal()
    try:
        store_embedding_data(db=db, user_id=user_id)
        logger.info(f"Finished embedding task for user {user_id}")

    except Exception as e:
        logger.exception(f"Failed embedding task for user {user_id}: {e}")
        raise e

    finally:
        db.close()