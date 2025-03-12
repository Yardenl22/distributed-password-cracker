import aio_pika
import asyncio
import json
import os
from src.common import CustomLogger, connection_manager

logger = CustomLogger(component='RESULT_LISTENER')
RESULTS_FILE_PATH = "results.json"


async def _save_results(results: dict[str, str]):
    if not os.path.exists(RESULTS_FILE_PATH):
        with open(RESULTS_FILE_PATH, "w", encoding='utf-8') as f:
            json.dump([], f, indent=4)

    new_results = [{"hash": hash_key, "password": password} for hash_key, password in results.items()]

    with open(RESULTS_FILE_PATH, "r+", encoding='utf-8') as f:
        existing_data = json.load(f)
        existing_data.extend(new_results)
        f.seek(0)
        json.dump(existing_data, f, indent=4)


async def process_results(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            task = json.loads(message.body.decode())
            task_id: str = task['task_id']
            results: dict[str, str] = task.get('results', {})

            await _save_results(results)

            logger.info(f'Received result for task {task_id}: {results.items()}')

            await connection_manager.redis_adapter.delete_task(task_id)
            logger.info(f"Task {task_id} deleted from Redis after processing")

            await message.ack()

        except Exception as e:
            logger.error(f'Failed to process result message: {str(e)}')
            await message.nack(requeue=True)



async def result_listener_loop():
    try:
        logger.info("Initializing Redis & RabbitMQ connections...")
        await connection_manager.connect_redis()
        await connection_manager.connect_rabbitmq()

        connection = connection_manager.rabbitmq_adapter.rabbit_connection
        channel = await connection.channel()
        queue = await channel.declare_queue("results_queue", durable=True)

        logger.info("Result listener started, waiting for messages...")

        while True:
            try:
                await queue.consume(process_results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in result listener loop: {str(e)}")
                await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"Failed to start result listener: {str(e)}")
    finally:
        logger.info("Closing connections...")
        await connection_manager.close_connections()


if __name__ == "__main__":
    asyncio.run(result_listener_loop())
