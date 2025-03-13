from abc import ABC, abstractmethod
from src.common.models import CrackedPassword


class BaseStorage(ABC):
    @abstractmethod
    async def save_results(self, results: list[CrackedPassword]):
        ...

    @abstractmethod
    async def get_results(self) -> list[CrackedPassword]:
        ...

    @abstractmethod
    async def get_password_by_hash(self, hash_value: str) -> str:
        ...

    @abstractmethod
    async def search_passwords(self, query: str) -> list[CrackedPassword]:
        ...
