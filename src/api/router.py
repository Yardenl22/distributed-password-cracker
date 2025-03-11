import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.common import CustomLogger
from src.common.models import TaskCreate, TaskStatusResponse

router = APIRouter()
logger = CustomLogger(component='MASTER')

limiter = Limiter(key_func=get_remote_address)

tasks: dict[int, TaskStatusResponse] = {}


async def _process_json_file(file: UploadFile) -> list[str]:
    try:
        content = await file.read()
        data = json.loads(content)
        hashes = data.get('hashes', [])

        if not isinstance(hashes, list) or not all(isinstance(h, str) for h in hashes):
            raise ValueError('Invalid JSON format')

        return hashes
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Invalid JSON file: {str(e)}')


async def _process_txt_file(file: UploadFile) -> list[str]:
    try:
        content = await file.read()
        return content.decode('utf-8').splitlines()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Invalid text file: {str(e)}')


@router.post('/upload_hashes', response_model=TaskStatusResponse)
@limiter.limit('10/minute')
def upload_hashes(request: Request, task: TaskCreate):
    task_id = len(tasks) + 1
    tasks[task_id] = TaskStatusResponse(task_id=task_id, status='queued')
    logger.info(f'New task received: {task_id} | Hashes: {task.hashes}')
    return tasks[task_id]


@router.post('/upload_file', response_model=TaskStatusResponse)
@limiter.limit('5/minute')
async def upload_file(
    request: Request,
    file: UploadFile = File(..., description='Supported file types: .json (hashes: list of hashes) or .txt (one hash per line)')
):
    if file.content_type == 'application/json':
        hashes = await _process_json_file(file)

    elif file.content_type == 'text/plain':
        hashes = await _process_txt_file(file)

    else:
        raise HTTPException(status_code=400, detail='Only .json or .txt files are allowed')

    task_id = len(tasks) + 1
    tasks[task_id] = TaskStatusResponse(task_id=task_id, status='queued')
    logger.info(f'New task received from file: {task_id} | Hashes: {hashes}')
    return tasks[task_id]


@router.post('/start_cracking/{task_id}', response_model=TaskStatusResponse, include_in_schema=False)
@limiter.limit('5/minute')
def start_cracking(request: Request, task_id: int):
    if task_id not in tasks:
        return {'error': 'Task not found'}

    tasks[task_id].status = 'in_progress'
    logger.info(f'Task {task_id} started')
    return tasks[task_id]


@router.get('/task_status/{task_id}', response_model=TaskStatusResponse)
@limiter.limit('20/minute')
def task_status(request: Request, task_id: int):
    if task_id not in tasks:
        return {'error': 'Task not found'}

    return tasks[task_id]
