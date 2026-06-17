from fastapi import FastAPI

app = FastAPI(title="Environmental Metrics Ingestion Service")


@app.get("/")
def root():
    return {"status": "ok"}