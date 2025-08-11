"""Factory for Celery application used by background workers."""

from celery import Celery
from celery.signals import task_failure
from prometheus_client import Counter
import json
from datetime import datetime
import redis

from .config import get_settings
from .scheduler import setup_periodic_tasks
from .telemetry import setup_telemetry
from .tracing import setup_tracing
from opentelemetry.instrumentation.celery import CeleryInstrumentor

settings = get_settings()
setup_telemetry("moodswing-trading-worker")
CeleryInstrumentor().instrument()

# Initialize OpenTelemetry tracing for Celery workers and producers
setup_tracing(service_name="moodswing-celery")

REDIS = redis.Redis.from_url(settings.redis_url)
DEAD_LETTER_KEY = "celery:dead_letter"
DEAD_LETTER_TTL = 7 * 24 * 60 * 60  # 7 days

celery_app = Celery(
    "moodswing_trading",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_send_sent_event=True,
)

# OpenTelemetry: instrument Celery publish/consume paths
try:
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    CeleryInstrumentor().instrument()
except Exception:
    # Best-effort; worker continues even if instrumentation isn't available
    pass

TASK_FAILURES = Counter(
    "task_failures_total",
    "Total Celery task failures",
    ["task_name"],
)


@task_failure.connect
def _handle_failure(sender=None, task_id=None, args=None, kwargs=None, einfo=None, **_: object) -> None:
    """Increment Prometheus counter and persist failed payloads."""
    name = getattr(sender, "name", str(sender)) if sender else "unknown"
    TASK_FAILURES.labels(name).inc()
    try:
        payload = {
            "task_id": task_id,
            "task_name": name,
            "args": args,
            "kwargs": kwargs,
            "exception": str(einfo.exception) if einfo else "",
            "timestamp": datetime.utcnow().isoformat(),
        }
        REDIS.rpush(DEAD_LETTER_KEY, json.dumps(payload))
        REDIS.expire(DEAD_LETTER_KEY, DEAD_LETTER_TTL)
    except Exception:
        # best effort; avoid crashing signal handler
        pass


setup_periodic_tasks(celery_app)

__all__ = ["celery_app"]