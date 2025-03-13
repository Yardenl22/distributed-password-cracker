import json
import aiofiles
from pathlib import Path

from src.storage.base import BaseStorage
from src.common.models import CrackedPassword


class JSONStorage(BaseStorage):
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()


    def _ensure_storage_exists(self):
        if not self.storage_path.exists() or not self.storage_path.read_text(encoding='utf-8').strip():
            with self.storage_path.open('w', encoding='utf-8') as f:
                json.dump([], f, indent=4)


    async def _load_existing_data(self) -> list[CrackedPassword]:
        async with aiofiles.open(self.storage_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content) if content else []
            return [CrackedPassword(**item) for item in data]


    async def save_results(self, results: dict[str, str]):
        new_results = [CrackedPassword(hash=hash_key, password=password) for hash_key, password in results.items()]

        existing_data = await self._load_existing_data()
        existing_hashes = {entry.hash for entry in existing_data}

        non_duplicate_results = [result for result in new_results if result.hash not in existing_hashes]
        all_results = existing_data + non_duplicate_results

        serialized_data = [item.model_dump() for item in all_results]

        async with aiofiles.open(self.storage_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(serialized_data, indent=4))


    async def get_results(self) -> list[CrackedPassword]:
        return await self._load_existing_data()


    async def get_password_by_hash(self, hash_value: str) -> str | None:
        existing_data = await self._load_existing_data()
        for entry in existing_data:
            if entry.hash == hash_value:
                return entry.password
        return None


    async def search_passwords(self, query: str) -> list[CrackedPassword]:
        existing_data = await self._load_existing_data()
        return [entry for entry in existing_data if query.lower() in entry.password.lower()]
