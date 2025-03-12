import json
import aio_pika
from src.common import CustomLogger

logger = CustomLogger(component='RABBITMQ')


class RabbitMQAdapter:
    def __init__(self, rabbit_url: str = 'amqp://guest:guest@localhost:5672/'):
        self.rabbit_url = rabbit_url
        self.rabbit_connection = None
        self.rabbit_channel = None


    async def connect(self):
        try:
            self.rabbit_connection = await aio_pika.connect_robust(self.rabbit_url)
            self.rabbit_channel = await self.rabbit_connection.channel()
            logger.info('Connected to RabbitMQ')
        except Exception as e:
            logger.error(f'RabbitMQ connection failed: {str(e)}')


    async def close(self):
        try:
            if self.rabbit_connection:
                await self.rabbit_connection.close()
                logger.info('RabbitMQ connection closed')
        except Exception as e:
            logger.error(f'RabbitMQ close failed: {str(e)}')


    async def send_task(self, queue_name: str, task_data: dict):
        try:
            queue = await self.rabbit_channel.declare_queue(queue_name, durable=True)
            message = aio_pika.Message(body=json.dumps(task_data).encode())
            await queue.channel.default_exchange.publish(message, routing_key=queue_name)
            logger.info(f"Task {task_data['task_id']} sent to queue: {queue_name}")
        except Exception as e:
            logger.error(f"RabbitMQ send_task failed: {str(e)}")
