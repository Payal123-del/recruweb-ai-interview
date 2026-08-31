import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.exceptions import AppException
from app.api.v1.api_router import api_router
from app.db.init_db import init_db

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [ReqID: %(name)s] %(message)s"
)
logger = logging.getLogger("ardhnarishwar")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schemas and running bootstrap...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await init_db(session)
    logger.info("Ardhnarishwar AI SaaS platform backend ready.")
    yield
    logger.info("Shutting down Ardhnarishwar backend...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise Multi-Tenant AI Robotics Interview SaaS Platform",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Logging & Tracing Middleware
@app.middleware("http")
async def logging_and_tracing_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    latency_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(latency_ms)

    logger.info(
        f"{request.method} {request.url.path} | Status: {response.status_code} | Duration: {latency_ms}ms | Client: {request.client.host if request.client else 'unknown'}"
    )
    return response


# Global Exception Handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error": exc.code,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred. Our engineering team has been notified.",
            "error": "INTERNAL_SERVER_ERROR"
        }
    )


# Health and Observability Probes
@app.get("/health", tags=["Observability"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "engine_version": settings.EVALUATION_ENGINE_VERSION
    }


@app.get("/ready", tags=["Observability"])
async def readiness_check():
    # Verify DB connectivity
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ready" if db_status == "connected" else "degraded",
        "database": db_status,
        "storage": settings.STORAGE_PROVIDER
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
