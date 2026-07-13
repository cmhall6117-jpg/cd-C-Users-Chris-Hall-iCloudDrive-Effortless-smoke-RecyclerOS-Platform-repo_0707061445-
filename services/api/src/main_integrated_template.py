from fastapi import FastAPI

app = FastAPI(title="RecyclerOS Platform API", version="0.1.0")

@app.get("/v1/health")
def health_check():
    return {"status": "ok", "service": "recycleros-api", "version": "0.1.0"}

# Register merged vertical slice routers here.
