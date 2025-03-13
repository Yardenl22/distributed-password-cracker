import json
import redis.asyncio as redis

from src.common.logger import CustomLogger


logger = CustomLogger(component='REDIS')


class RedisAdapter:
    def __init__(self, redis_url: str):
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
            await self.redis.set(f'task:{task_id}', json.dumps(task_data))
            logger.info(f'Task {task_id} stored in Redis')

        except Exception as e:
            logger.error(f'Redis set_task failed: {str(e)}')


    async def get_task(self, task_id: str) -> dict:
        try:
            task_json = await self.redis.get(f'task:{task_id}')
            if task_json:
                return json.loads(task_json)

        except Exception as e:
            logger.error(f'Redis get_task failed: {str(e)}')


    async def delete_task(self, task_id: str):
        try:
            await self.redis.delete(f'task:{task_id}')
            logger.info(f'Task {task_id} deleted from Redis')
        except Exception as e:
            logger.error(f'Failed to delete task {task_id} from Redis: {str(e)}')
