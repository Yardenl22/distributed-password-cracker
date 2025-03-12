import redis.asyncio as redis
import json
from src.common import CustomLogger

logger = CustomLogger(component='REDIS')

class RedisAdapter:
    def __init__(self, redis_url: str = 'redis://localhost:6379'):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        try:
            self.redis = redis.Redis.from_url(self.redis_url, decode_responses=True)
            logger.info('Connected to Redis')
        except Exception as e:
            logger.error(f'Redis connection failed: {str(e)}')

    async def close(self):
        try:
            if self.redis:
                await self.redis.close()
                logger.info('Redis connection closed')
        except Exception as e:
            logger.error(f'Redis close failed: {str(e)}')

    async def set_task(self, task_id: str, status: str, hashes: list[str]):
        try:
            task_data = {'task_id': task_id, 'status': status, 'hashes': hashes}
            await self.redis.set(f"task:{task_id}", json.dumps(task_data))
            logger.info(f"Task {task_id} stored in Redis")

        except Exception as e:
            logger.error(f"Redis set_task failed: {str(e)}")

    async def get_task(self, task_id: str):
        try:
            task_json = await self.redis.get(f"task:{task_id}")
            if task_json:
                return json.loads(task_json)
            return None

        except Exception as e:
            logger.error(f"Redis get_task failed: {str(e)}")
            return None

    async def get_keys(self, pattern: str):
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Redis get_keys failed: {str(e)}")
            return []

    async def update_task_status(self, task_id: str, status: str, result: str = ""):
        try:
            task = await self.get_task(task_id)

            if task:
                task["status"] = status
                task["result"] = result
                await self.redis.set(f"task:{task_id}", json.dumps(task))
                logger.info(f"Task {task_id} updated to status: {status}")
        except Exception as e:
            logger.error(f"Redis update_task_status failed: {str(e)}")
