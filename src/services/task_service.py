import redis
import aio_pika.exceptions
from fastapi import HTTPException

from src.common.config import config
from src.common.logger import CustomLogger
from src.common.connection_manager import connection_manager
from src.storage.storage_factory import storage
from src.common.models import Task, TaskStatusEnum


CHUNK_SIZE: int = config.API.TASK_CHUNK_SIZE

logger = CustomLogger(component='INTERNAL_API')


async def submit_task(hashes: list[str]) -> list[Task]:
    try:
        existing_results = await storage.get_results()
        existing_hashes = {entry.hash for entry in existing_results}
        new_hashes = [hash for hash in hashes if hash not in existing_hashes]

        if not new_hashes:
            return []

        tasks = [
            Task(hashes=new_hashes[i : i + CHUNK_SIZE])
            for i in range(0, len(new_hashes), CHUNK_SIZE)
        ]

        for task in tasks:
            await connection_manager.redis_adapter.set_task(task.id, TaskStatusEnum.PROCESSING, task.hashes)
            logger.info(f'Task {task.id} created and queued')
            await connection_manager.rabbitmq_adapter.send_task('tasks_queue', task.model_dump())
            logger.info(f'Task {task.id} send successfully to tasks_queue')

        return tasks

    except redis.exceptions.ConnectionError as e:
        logger.error(f'Redis connection error: {str(e)}')
        raise HTTPException(status_code=500, detail='Failed to connect to Redis')

    except redis.exceptions.RedisError as e:
        logger.error(f'Redis error: {str(e)}')
        raise HTTPException(status_code=500, detail='Redis operation failed')

    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f'RabbitMQ connection error: {str(e)}')
        raise HTTPException(status_code=500, detail='Failed to connect to RabbitMQ')

    except aio_pika.exceptions.AMQPChannelError as e:
        logger.error(f'RabbitMQ channel error: {str(e)}')
        raise HTTPException(status_code=500, detail='RabbitMQ channel error')

    except aio_pika.exceptions.AMQPError as e:
        logger.error(f'RabbitMQ error: {str(e)}')
        raise HTTPException(status_code=500, detail='RabbitMQ operation failed')

    except Exception as e:
        logger.error(f'Failed to submit task: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')
