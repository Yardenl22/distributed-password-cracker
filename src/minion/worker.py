import aio_pika
import asyncio
import hashlib
import json
from src.common import CustomLogger, connection_manager


logger = CustomLogger(component='WORKER')


async def _generate_hashes(prefixes: list[str], hashes: list[str]):
    found_results = {h: '' for h in hashes}

    for prefix in prefixes:
        for i in range(0, 10000000):
            password = f"{prefix}-{i:07d}"
            md5_hash = hashlib.md5(password.encode()).hexdigest()

            if md5_hash in hashes:
                found_results[md5_hash] = password

            if sum(1 for v in found_results.values() if v) >= 5:
                return found_results


    return found_results


async def _crack_hash(hashes: list[str]) -> dict[str, str]:
    prefixes = ["050", "051", "052", "053", "054", "055", "056", "057", "058", "059"]
    results = await _generate_hashes(prefixes, hashes)
    return results


async def process_task(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            task = json.loads(message.body.decode())
            task_id = task["id"]
            hashes = task["hashes"]
            logger.info(f"Processing task {task_id} with {len(hashes)} hashes")
            cracked_results = await _crack_hash(hashes)

            queue = await connection_manager.rabbitmq_adapter.rabbit_channel.declare_queue("results_queue", durable=True)
            response_message = aio_pika.Message(body=json.dumps({"task_id": task_id, "results": cracked_results}).encode())
            await queue.channel.default_exchange.publish(response_message, routing_key="results_queue")
            logger.info(f"Finish Processing task {task_id}, results saved.")

        except Exception as e:
            logger.error(f"Worker processing failed: {str(e)}")
            await message.nack(requeue=True)


async def worker_loop():
    try:
        logger.info("Initializing Redis & RabbitMQ connections...")
        await connection_manager.connect_redis()
        await connection_manager.connect_rabbitmq()

        connection = connection_manager.rabbitmq_adapter.rabbit_connection
        channel = await connection.channel()
        queue = await channel.declare_queue("tasks_queue", durable=True)

        logger.info("Worker started, waiting for tasks...")

        while True:
            try:
                await queue.consume(process_task)
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")
                await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"Worker encountered an error: {str(e)}")

    finally:
        logger.info("Closing connections...")
        await connection_manager.close_connections()


if __name__ == "__main__":
    asyncio.run(worker_loop())
