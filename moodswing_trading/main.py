from fastapi import FastAPI, Request, status
from api import company, market, news, predict, sentiment
from fastapi.responses import PlainTextResponse, JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from models import ProblemDetails
from db.models import init_db
import uuid

app = FastAPI()
init_db()

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

app.include_router(market.router)
app.include_router(news.router)
app.include_router(predict.router)
app.include_router(sentiment.router)
app.include_router(company.router)

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

def problem_response(title, status_code, detail=None):
    trace_id = str(uuid.uuid4())
    problem = ProblemDetails(
        title=title,
        status=status_code,
        detail=detail,
        trace_id=trace_id
    )
    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump(),
        media_type="application/problem+json"
    )

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):
    return problem_response("ValidationError", 400, str(exc))