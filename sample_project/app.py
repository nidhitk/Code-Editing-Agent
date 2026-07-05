from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/helloworld")
def get_hello_world():
    return {"message": "Hello World"}