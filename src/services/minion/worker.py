import aio_pika
import asyncio
import json

from src.common.logger import CustomLogger
from src.common.connection_manager import connection_manager
from src.services.minion import hash_cracker

logger = CustomLogger(component='WORKER')


async def _process_task(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            task = json.loads(message.body.decode())
            task_id = task['id']
            hashes = task['hashes']
            logger.info(f'Processing task {task_id}')

            cracked_results = await hash_cracker.crack_hashes(hashes)

            channel = connection_manager.rabbitmq_adapter.channel
            result_queue = await channel.declare_queue('results_queue', durable=True)
            response_message = aio_pika.Message(body=json.dumps({'task_id': task_id, 'results': cracked_results}).encode())
            await channel.default_exchange.publish(response_message, routing_key=result_queue.name)

            logger.info(f'Finish Processing task {task_id}')

        except Exception as e:
            logger.error(f'Worker processing failed: {str(e)}', exc_info=True)
            await message.nack(requeue=True)


async def worker_loop():
    try:
        logger.info('Initializing Redis & RabbitMQ connections...')
        await connection_manager.connect_redis()
        await connection_manager.connect_rabbitmq()

        channel = connection_manager.rabbitmq_adapter.channel
        queue = await channel.declare_queue('tasks_queue', durable=True)

        logger.info('Worker started, waiting for tasks...')

        await queue.consume(_process_task)
        await asyncio.Future()

    except Exception as e:
        logger.error(f'Worker encountered an error: {str(e)}', exc_info=True)
    finally:
        logger.info('Closing connections...')
        await connection_manager.close_connections()

def run_worker():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(worker_loop())
    except Exception as e:
        logger.error(f'Worker encountered an error: {str(e)}', exc_info=True)
    finally:
        loop.close()

if __name__ == '__main__':
    run_worker()
