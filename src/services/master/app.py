import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.common.config import config
from src.common.connection_manager import connection_manager
from src.common.logger import CustomLogger
from src.services.master.router import router


HOST: str = config.SERVICE.HOST
PORT: int = config.SERVICE.PORT


logger = CustomLogger(component='MASTER')
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Initializing Redis & RabbitMQ connections...')
    await connection_manager.connect_redis()
    await connection_manager.connect_rabbitmq()
    app.state.limiter = limiter
    yield
    logger.info('Closing Redis & RabbitMQ connections...')
    await connection_manager.close_connections()


app = FastAPI(
    title='Distributed Password Cracker',
    description='An API for distributing password hash cracking tasks across multiple workers. '
                'Supports direct hash submission and file uploads (.json, .txt).',
    version='1.0.0',
    lifespan=lifespan
)

app.include_router(router)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get('/', include_in_schema=False)
def root_redirect():
    return RedirectResponse(url='/docs')


if __name__ == '__main__':
    logger.info('Starting Master API...')
    uvicorn.run(app, host=HOST, port=PORT)
