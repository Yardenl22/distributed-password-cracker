import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.api import router
from src.common import CustomLogger

logger = CustomLogger(component='MASTER')

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title='Distributed Password Cracker',
    description='An API for distributing password hash cracking tasks across multiple workers. '
                'Supports direct hash submission and file uploads (.json, .txt).',
    version='1.0.0'
)
app.include_router(router)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please slow down."}
    )




@app.get('/')
def root_redirect():
    return RedirectResponse(url='/docs')


if __name__ == '__main__':
    logger.info('Starting Master API...')
    uvicorn.run(app, host='0.0.0.0', port=8080)
