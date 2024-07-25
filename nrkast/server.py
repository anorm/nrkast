from fastapi import FastAPI

from . import factory

app = FastAPI()

@app.get("/ping")
def ping():
    return "OK"
