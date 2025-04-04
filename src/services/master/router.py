import json
from http.client import responses

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.common.logger import CustomLogger
from src.common.connection_manager import connection_manager
from src.common.models import TaskStatusResponse, TaskRequest, Task
from src.services import task_service


router = APIRouter()
logger = CustomLogger(component='ROUTER')
limiter = Limiter(key_func=get_remote_address)


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


@router.post('/upload_hashes')
@limiter.limit('10/minute')
async def upload_hashes(request: Request, task_request: TaskRequest):
    try:
        tasks: list[Task] = await task_service.submit_task(task_request.hashes)

        if not tasks:
            return {'Message': 'Sent hashes already calculated'}

        response = [
            {
                'message': 'Hashes sent to decryption',
                'Tasks': {
                    "id": task.id,
                    'Hashes': task.hashes
                }
            }
            for task in tasks
        ]
        return response

    except Exception as e:
        logger.error(f'Failed to upload hashes: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')


@router.post('/upload_file')
@limiter.limit('5/minute')
async def upload_file(
        request: Request,
        file: UploadFile = File(
            ...,
            description='Supported file types: .json (hashes: list of hashes) or .txt (one hash per line)')
):
    try:
        if file.content_type == 'application/json':
            hashes = await _process_json_file(file)

        elif file.content_type == 'text/plain':
            hashes = await _process_txt_file(file)

        else:
            raise HTTPException(status_code=400, detail='Only .json or .txt files are allowed')

        tasks: list[Task] = await task_service.submit_task(hashes)
        response = [
            {
                'message': 'Hashes sent to decryption',
                'Tasks': {
                    "id": task.id,
                    'Hashes': task.hashes
                }
            }
            for task in tasks
        ]
        return response

    except Exception as e:
        logger.error(f'Failed to upload file: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')


@router.get('/task_status/{task_id}', response_model=TaskStatusResponse)
@limiter.limit('20/minute')
async def task_status(request: Request, task_id: str):
    try:
        task: dict = await connection_manager.redis_adapter.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail='Task not found')

        task_response = TaskStatusResponse(task_id=task_id, status=task['status'])
        return task_response

    except Exception as e:
        error = str(e)
        logger.error(f'Failed to get task status: {error}')
        raise HTTPException(status_code=404, detail=error)
