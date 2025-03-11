import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/")
def health_check():
    return {'status': 'alive'}


@app.get('/', include_in_schema=False)
def root_redirect():
    return RedirectResponse(url='/docs')


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8080)
