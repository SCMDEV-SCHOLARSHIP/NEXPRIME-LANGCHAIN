from dependency_injector.wiring import Provide
from qdrant_client import AsyncQdrantClient

from app.schemas.collection_schema import CollectionResponseDTO


class CollectionService:

    def __init__(self, url: str = Provide["config.vectorstore.url"]) -> None:
        self.qdrant_client = AsyncQdrantClient(url)

    async def get_collections(self) -> list[CollectionResponseDTO]:
        results = await self.qdrant_client.get_collections()
        collections = [CollectionResponseDTO(collection_name=collection_description.name) for collection_description in results.collections]
        return collections
