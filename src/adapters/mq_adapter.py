import json
import aio_pika

from src.common.logger import CustomLogger

logger = CustomLogger(component='RABBITMQ')


class RabbitMQAdapter:
    def __init__(self, rabbit_url: str):
        self.rabbit_url = rabbit_url
        self.connection = None
        self.channel = None

    async def connect(self):
        if self.connection and not self.connection.is_closed:
            return

        try:
            self.connection = await aio_pika.connect_robust(self.rabbit_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            logger.info('Connected to RabbitMQ')
        except Exception as e:
            logger.error(f'RabbitMQ connection failed: {str(e)}')

    async def close(self):
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info('RabbitMQ connection closed')
        except Exception as e:
            logger.error(f'RabbitMQ close failed: {str(e)}')

    async def send_task(self, queue_name: str, task_data: dict):
        await self.connect()

        try:
            message = aio_pika.Message(body=json.dumps(task_data).encode())
            await self.channel.default_exchange.publish(message, routing_key=queue_name)
            logger.info(f"Task {task_data['id']} sent to queue: {queue_name}")
        except Exception as e:
            logger.error(f'RabbitMQ send_task failed: {str(e)}')
