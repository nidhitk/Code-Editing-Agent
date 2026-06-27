from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello_world():
    return {"message": "hello"}