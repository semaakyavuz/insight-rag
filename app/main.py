from fastapi import FastAPI

app = FastAPI(title="insight-rag")


@app.get("/health")
def health_check():
    return {"status": "ok"}
