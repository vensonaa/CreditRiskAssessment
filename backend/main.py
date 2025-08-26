from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="Credit Risk Assessment API",
    description="AI-powered credit risk assessment system with LangGraph workflow",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Credit Risk Assessment API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "credit-risk-assessment"}

if __name__ == "__main__":
    import uvicorn
    # Use import string for reload to work properly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
