from fastapi import APIRouter, HTTPException
from src.common import CustomLogger, connection_manager
from src.common.models import Task, TaskStatusEnum

internal_router = APIRouter()
logger = CustomLogger(component='INTERNAL_API')

CHUNK_SIZE = 5

@internal_router.post('/submit_task', include_in_schema=False)
async def submit_task(hashes: list[str]):
    try:
        tasks = [Task(hashes=hashes[i:i + CHUNK_SIZE]) for i in range(0, len(hashes), CHUNK_SIZE)]

        for task in tasks:
            await connection_manager.redis_adapter.set_task(task.id, TaskStatusEnum.QUEUED, task.hashes)
            logger.info(f'Task {task.id} created and queued')
            await connection_manager.rabbitmq_adapter.send_task('tasks_queue', task.model_dump())
            logger.info(f'Task {task.id} send successfully to tasks_queue')

    except Exception as e:
        logger.error(f"Failed to submit task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
