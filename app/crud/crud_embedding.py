from app.models.embedding import Embeddings
from app.crud.base import CRUDBase

crud_embedding = CRUDBase[Embeddings](Embeddings)