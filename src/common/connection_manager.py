from src.common import CustomLogger
from src.common.mq_adapter import RabbitMQAdapter
from src.common.redis_adapter import RedisAdapter


logger = CustomLogger(component='CONNECTION_MANAGER')

class ConnectionManager:
    def __init__(self, redis_url: str = 'redis://localhost:6379', rabbit_url: str = 'amqp://guest:guest@localhost:5672/'):
        self.redis_adapter = RedisAdapter(redis_url)
        self.rabbitmq_adapter = RabbitMQAdapter(rabbit_url)

    async def connect_redis(self):
        try:
            await self.redis_adapter.connect()
            logger.info('Connected to Redis')
        except Exception as e:
            logger.error(f'Redis connection failed: {str(e)}')

    async def connect_rabbitmq(self):
        try:
            await self.rabbitmq_adapter.connect()
            logger.info('Connected to RabbitMQ')
        except Exception as e:
            logger.error(f'RabbitMQ connection failed: {str(e)}')

    async def close_connections(self):
        try:
            await self.redis_adapter.close()
            await self.rabbitmq_adapter.close()
            logger.info('Connections closed')
        except Exception as e:
            logger.error(f'Failed to close connections: {str(e)}')


connection_manager = ConnectionManager()
