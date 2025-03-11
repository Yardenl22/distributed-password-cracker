from fastapi import APIRouter
from src.common.models import TaskCreate, TaskStatusResponse
from src.common import CustomLogger

router = APIRouter()
logger = CustomLogger(component='MASTER')

tasks: dict[int, TaskStatusResponse] = {}


@router.post('/upload_hashes', response_model=TaskStatusResponse)
def upload_hashes(task: TaskCreate):
    task_id = len(tasks) + 1
    tasks[task_id] = TaskStatusResponse(task_id=task_id, status='queued')
    logger.info(f'New task received: {task_id} | Hashes: {task.hashes}')
    return tasks[task_id]

@router.post('/start_cracking/{task_id}', response_model=TaskStatusResponse, include_in_schema=False)
def start_cracking(task_id: int):
    if task_id not in tasks:
        return {'error': 'Task not found'}

    tasks[task_id].status = 'in_progress'
    logger.info(f'Task {task_id} started')
    return tasks[task_id]


@router.get('/task_status/{task_id}', response_model=TaskStatusResponse)
def task_status(task_id: int):
    if task_id not in tasks:
        return {'error': 'Task not found'}

    return tasks[task_id]
