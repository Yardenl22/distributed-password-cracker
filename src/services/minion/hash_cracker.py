import time
import hashlib
import asyncio

from src.common.config import config
from src.common.logger import CustomLogger


PREFIXES: list[str] = config.WORKER.PREFIXES

logger = CustomLogger(component='HASH_CRACKER')

stop_event = asyncio.Event()


async def _generate_hashes_for_prefix(prefix: str, hashes: list[str], found_results: dict[str, str]):
    for i in range(0, 10000000):
        if stop_event.is_set():
            return

        password = f'{prefix}-{i:07d}'
        md5_hash = hashlib.md5(password.encode()).hexdigest()

        if md5_hash in hashes and not found_results.get(md5_hash, ''):
            found_results[md5_hash] = password

        if sum(1 for v in found_results.values() if v) >= 5:
            stop_event.set()
            return


async def crack_hashes(hashes: list[str]) -> dict[str, str]:
    logger.info(f'Starting hash cracking for {len(hashes)} hashes...')
    stop_event.clear()
    start_time = time.time()

    found_results = {h: '' for h in hashes}

    tasks = [
        asyncio.create_task(_generate_hashes_for_prefix(prefix, hashes, found_results))
        for prefix in PREFIXES
    ]

    await asyncio.gather(*tasks)

    duration = time.time() - start_time
    logger.info(f'Finished hash cracking. Found {len([v for v in found_results.values() if v])} matches. Duration: {duration}')

    return found_results
