import json

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.internal_router import submit_task
from src.common import CustomLogger, connection_manager
from src.common.models import TaskStatusResponse, TaskRequest

external_router = APIRouter()
logger = CustomLogger(component='EXTERNAL_API')
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


@external_router.post('/upload_hashes')
@limiter.limit('10/minute')
async def upload_hashes(request: Request, task_request: TaskRequest):
    try:
        await submit_task(task_request.hashes)
        response = {
            'message': 'Cracking has started',
            'hashes': task_request.hashes
        }
        return response

    except Exception as e:
        logger.error(f'Failed to upload hashes: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')


@external_router.post('/upload_file')
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

        await submit_task(hashes)

        response = {
            'message': 'Calculation has started',
            'hashes': hashes
        }
        return response

    except Exception as e:
        logger.error(f'Failed to upload file: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')


@external_router.get('/task_status/{task_id}', response_model=TaskStatusResponse)
@limiter.limit('20/minute')
async def task_status(request: Request, task_id: str):
    try:
        task: dict = await connection_manager.redis_adapter.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail='Task not found')

        task_response = TaskStatusResponse(task_id=task_id, status=task['status'])
        return task_response

    except Exception as e:
        logger.error(f'Failed to get task status: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')
