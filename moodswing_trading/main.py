from fastapi import FastAPI, Request, status
from api import company, market, news, predict, sentiment
from fastapi.responses import PlainTextResponse, JSONResponse
from models import ProblemDetails
import uuid

app = FastAPI()

app.include_router(market.router)
app.include_router(news.router)
app.include_router(predict.router)
app.include_router(sentiment.router)
app.include_router(company.router)

@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "healthy"

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return "# Prometheus metrics stub\n"

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

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return problem_response("NotFound", 404, str(exc))

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return problem_response("RateLimitExceeded", 429, str(exc))

@app.exception_handler(502)
async def upstream_error_handler(request: Request, exc):
    return problem_response("UpstreamError", 502, str(exc))

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return problem_response("InternalServerError", 500, str(exc))