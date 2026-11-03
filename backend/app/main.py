from fastapi import FastAPI

app = FastAPI(
    title="HEAT-EWS API",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "project": "HEAT-EWS",
        "location": "Abu Dhabi, UAE"
    }