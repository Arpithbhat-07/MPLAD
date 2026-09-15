from fastapi import FastAPI

app = FastAPI(
    title="MPLADS Monitor API",
    description="AI-powered monitoring backend for MPLADS",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "MPLADS Monitor API is running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }