import hashlib

from src.common.config import config
from src.common.logger import CustomLogger


PREFIXES: list[str] = config.WORKER.PREFIXES

logger = CustomLogger(component='HASH_CRACKER')

async def _generate_hashes(prefixes: list[str], hashes: list[str]) -> dict[str, str]:
    found_results = {h: '' for h in hashes}

    for prefix in prefixes:
        for i in range(0, 10000000):
            password = f'{prefix}-{i:07d}'
            md5_hash = hashlib.md5(password.encode()).hexdigest()

            if md5_hash in hashes:
                found_results[md5_hash] = password

            if sum(1 for v in found_results.values() if v) >= 5:
                return found_results


    return found_results


async def crack_hashes(hashes: list[str]) -> dict[str, str]:
    logger.info(f'Starting hash cracking for {len(hashes)} hashes...')
    results = await _generate_hashes(PREFIXES, hashes)
    logger.info(f'Finished hash cracking. Found {len([v for v in results.values() if v])} matches.')
    return results
