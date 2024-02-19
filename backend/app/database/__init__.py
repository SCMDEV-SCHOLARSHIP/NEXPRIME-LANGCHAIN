from abc import ABC, abstractmethod
from typing import Any
from langchain_core.documents import Document


class CRUD(ABC):
    @abstractmethod
    def create(self, documents: list[Document], **kwargs: Any) -> list[str]:
        """Create vectors

        Returns:
            list[str]: list of ids in uuid
        """
