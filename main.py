from fastapi import FastAPI

app = FastAPI()


@app.get("/healthy")
def healthy_check():
    return {"status": "Healthy"}
