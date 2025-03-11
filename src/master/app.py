import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api import router
from src.common import CustomLogger

app = FastAPI()
app.include_router(router)
logger = CustomLogger(component="MASTER")


@app.get("/health_check")
def health_check():
    return {'status': 'alive'}


@app.get('/', include_in_schema=False)
def root_redirect():
    return RedirectResponse(url='/docs')


if __name__ == '__main__':
    logger.info("Starting Master API...")
    uvicorn.run(app, host='0.0.0.0', port=8080)
