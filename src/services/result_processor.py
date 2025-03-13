import aio_pika
import asyncio
import json

from src.common.logger import CustomLogger
from src.common.connection_manager import connection_manager
from src.storage.storage_factory import storage


logger = CustomLogger(component='RESULT_LISTENER')

a = storage
b = 5

async def _process_results(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            task = json.loads(message.body.decode())
            task_id: str = task['task_id']
            results: dict[str, str] = task.get('results', {})

            await storage.save_results(results)

            logger.info(f'Received result for task {task_id}: {results.items()}')

            await connection_manager.redis_adapter.delete_task(task_id)
            logger.info(f'Task {task_id} deleted from Redis after processing')

        except Exception as e:
            logger.error(f'Failed to process result message: {str(e)}')
            await message.nack(requeue=True)



async def _result_listener_loop():
    try:
        logger.info('Initializing Redis & RabbitMQ connections...')
        await connection_manager.connect_redis()
        await connection_manager.connect_rabbitmq()

        queue_name = 'results_queue'
        channel = connection_manager.rabbitmq_adapter.channel

        queue = await channel.declare_queue(queue_name, durable=True)
        logger.info(f'Listening on queue: {queue_name}')

        await queue.consume(_process_results)
        await asyncio.Future()

    except Exception as e:
        logger.error(f'Failed to start result listener: {str(e)}')
    finally:
        logger.info('Closing connections...')
        await connection_manager.close_connections()


def run_result_processor():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_result_listener_loop())
    except Exception as e:
        logger.error(f'Result processor encountered an error: {str(e)}', exc_info=True)
    finally:
        loop.close()

if __name__ == '__main__':
    run_result_processor()
