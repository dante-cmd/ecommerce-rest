from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.routers import admin, auth, cart, orders, payments, products, reviews, users


settings = get_settings()
configure_logging()

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])

openapi_tags = [
    {"name": "auth", "description": "Authentication and token management"},
    {"name": "users", "description": "User profile operations"},
    {"name": "products", "description": "Product catalog and search"},
    {"name": "cart", "description": "Shopping cart management"},
    {"name": "orders", "description": "Order processing"},
    {"name": "payments", "description": "Payment simulation"},
    {"name": "reviews", "description": "Reviews and ratings"},
    {"name": "admin", "description": "Admin-only endpoints"},
    {"name": "health", "description": "Health and metrics"},
]

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    openapi_tags=openapi_tags,
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundException)
def not_found_handler(_: Request, exc: NotFoundException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(ForbiddenException)
def forbidden_handler(_: Request, exc: ForbiddenException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(BadRequestException)
def bad_request_handler(_: Request, exc: BadRequestException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(_: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.get("/metrics", tags=["health"])
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(products.router, prefix=settings.api_v1_prefix)
app.include_router(cart.router, prefix=settings.api_v1_prefix)
app.include_router(orders.router, prefix=settings.api_v1_prefix)
app.include_router(payments.router, prefix=settings.api_v1_prefix)
app.include_router(reviews.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)
