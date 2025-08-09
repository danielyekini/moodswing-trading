from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from api import company, market, news, predict, sentiment, system
from fastapi.responses import PlainTextResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from models import ProblemDetails
from core.logging import setup_logging
from core.config import get_settings
from core.ratelimit import rate_limit_middleware
from core.tracing import setup_tracing
import uuid
from db.models import engine
from db.ensure_partitions import ensure_default_partitions
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

setup_logging()
setup_tracing(service_name="moodswing-api")
settings = get_settings()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(rate_limit_middleware)

# OpenTelemetry: instrument FastAPI app (exclude common health/metrics paths)
FastAPIInstrumentor.instrument_app(app, excluded_urls="/metrics,/healthz")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint"],
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency",
    ["endpoint"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUEST_COUNT.labels(request.method, request.url.path).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(duration)
    return response


@app.on_event("startup")
async def on_startup() -> None:
    # Best-effort safeguard to ensure default partitions exist in the target DB
    try:
        ensure_default_partitions(engine)
    except Exception:
        # Do not block startup; detailed errors will show up on first use if any
        pass

app.include_router(market.router)
app.include_router(news.router)
app.include_router(predict.router)
app.include_router(sentiment.router)
app.include_router(company.router)
app.include_router(system.router)

@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "healthy"

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "MoodSwing Trading API"}

# --- Error Handlers ---

def problem_response(title, status_code, detail=None, errors=None):
    trace_id = str(uuid.uuid4())
    problem = ProblemDetails(
        title=title,
        status=status_code,
        detail=detail,
        trace_id=trace_id,
        errors=errors
    )
    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump(),
        media_type="application/problem+json"
    )

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):
    return problem_response("ValidationError", 400, str(exc))

@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    return problem_response(
        "ValidationError",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=exc.errors(),
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return problem_response(exc.detail or "HTTPException", exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return problem_response("Internal Server Error", 500, str(exc))