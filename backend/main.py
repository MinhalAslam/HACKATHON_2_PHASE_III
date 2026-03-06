from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import auth, tasks, chat
from src.middleware.security import add_security_middleware
from src.utils.logger import setup_logging
from datetime import datetime
import uvicorn

# Setup logging
setup_logging()

app = FastAPI(title="Todo Full-Stack Web Application API", version="1.0.0")

# Add CORS middleware (MUST be before security middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
add_security_middleware(app)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/api/{user_id}", tags=["tasks"])
app.include_router(chat.router, prefix="/api/{user_id}", tags=["chat"])

@app.get("/")
async def root():
    from src.utils.logger import app_logger
    app_logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Todo API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for container health monitoring"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)