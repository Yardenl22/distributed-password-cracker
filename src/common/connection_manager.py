from fastapi import HTTPException

from src.adapters import RabbitMQAdapter, RedisAdapter

from . import utils
from .logger import CustomLogger


REDIS_CONNECTION_STRING: str = utils.get_env_variable('REDIS_CONNECTION_STRING')
RABBITMQ_CONNECTION_STRING: str = utils.get_env_variable('RABBITMQ_CONNECTION_STRING')


logger = CustomLogger(component='CONNECTION_MANAGER')


class ConnectionManager:
    def __init__(self, redis_url: str = REDIS_CONNECTION_STRING, rabbit_url: str = RABBITMQ_CONNECTION_STRING):
        self.redis_adapter = RedisAdapter(redis_url)
        self.rabbitmq_adapter = RabbitMQAdapter(rabbit_url)


    async def connect_redis(self):
        try:
            await self.redis_adapter.connect()
            logger.info('Connected to Redis')
        except Exception as e:
            logger.error(f'Redis connection failed: {str(e)}')
            raise HTTPException(status_code=503, detail="Failed to connect to Redis")


    async def connect_rabbitmq(self):
        try:
            await self.rabbitmq_adapter.connect()
            logger.info('Connected to RabbitMQ')
        except Exception as e:
            logger.error(f'RabbitMQ connection failed: {str(e)}')
            raise HTTPException(status_code=503, detail="Failed to connect to RabbitMQ")


    async def close_connections(self):
        try:
            await self.redis_adapter.close()
            await self.rabbitmq_adapter.close()
            logger.info('Connections closed')
        except Exception as e:
            logger.error(f'Failed to close connections: {str(e)}')


connection_manager = ConnectionManager()
