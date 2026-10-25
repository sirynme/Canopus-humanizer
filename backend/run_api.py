"""FastAPI Application Entry Point & ASGI Server Launcher."""

import os
import sys
from pathlib import Path

# Auto-resolve backend root and src directory into sys.path
backend_dir = Path(__file__).resolve().parent
src_dir = backend_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from turnitout.api.routes import router as api_router
from turnitout.config import GLOBAL_CONFIG

app = FastAPI(
    title="Turnitout Enterprise REST API",
    description="Deterministic AI Footprint Removal & Academic Citation Engine",
    version=GLOBAL_CONFIG.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root_status():
    return {
        "status": "online",
        "service": GLOBAL_CONFIG.APP_NAME,
        "version": GLOBAL_CONFIG.VERSION,
        "docs": "/docs",
        "endpoints": ["/v1/humanize", "/v1/citations", "/v1/quota", "/v1/health"]
    }


if __name__ == "__main__":
    import uvicorn
    # Default to 8080 to avoid collision with docs server on 8000
    port = int(os.getenv("API_PORT", 8080))
    print(f"\n🚀 Starting Turnitout Enterprise REST API on http://127.0.0.1:{port} ...")
    print(f"📖 Interactive Swagger API Documentation: http://127.0.0.1:{port}/docs\n")
    uvicorn.run("run_api:app", host="0.0.0.0", port=port, reload=False, app_dir=str(backend_dir))
