from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from dotenv import load_dotenv


_otel_initialized = False


def _parse_headers(headers_env: Optional[str]) -> Optional[Dict[str, str]]:
    if not headers_env:
        return None
    headers: Dict[str, str] = {}
    for pair in headers_env.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            headers[key.strip()] = value.strip()
    return headers


def setup_tracing(service_name: str, service_version: Optional[str] = None) -> None:
    """Initialize OpenTelemetry tracing with a 10% sampler and OTLP exporter.

    Exporter configuration is read from standard OTEL_* environment variables,
    notably:
      - OTEL_EXPORTER_OTLP_ENDPOINT or OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
      - OTEL_EXPORTER_OTLP_PROTOCOL ("grpc" or "http/protobuf")
      - OTEL_EXPORTER_OTLP_(TRACES_)HEADERS
      - OTEL_EXPORTER_OTLP_INSECURE
    """

    global _otel_initialized
    if _otel_initialized:
        return

    # Ensure values from the project's .env are available in process env
    try:
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
    except Exception:
        # Best-effort; proceed without .env
        pass

    resource_attrs = {SERVICE_NAME: service_name}
    if service_version:
        resource_attrs[SERVICE_VERSION] = service_version
    resource = Resource.create(resource_attrs)

    sampler = ParentBased(TraceIdRatioBased(0.10))
    provider = TracerProvider(resource=resource, sampler=sampler)

    protocol = (
        os.getenv("OTEL_EXPORTER_OTLP_TRACES_PROTOCOL")
        or os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL")
        or "grpc"
    ).lower()
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    headers = _parse_headers(
        os.getenv("OTEL_EXPORTER_OTLP_TRACES_HEADERS")
        or os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    )
    insecure = (os.getenv("OTEL_EXPORTER_OTLP_INSECURE") or "false").lower() in (
        "true",
        "1",
        "t",
        "yes",
    )

    # Select exporter based on requested protocol, with a safe fallback to gRPC
    try:
        if "http" in protocol:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter as HttpOTLPSpanExporter,
            )

            exporter = HttpOTLPSpanExporter(endpoint=endpoint, headers=headers)
        else:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter as GrpcOTLPSpanExporter,
            )

            exporter = GrpcOTLPSpanExporter(
                endpoint=endpoint, insecure=insecure, headers=headers
            )
    except Exception:
        # Fallback if protocol-specific import is unavailable
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter as GrpcOTLPSpanExporter,
        )

        exporter = GrpcOTLPSpanExporter(
            endpoint=endpoint, insecure=insecure, headers=headers
        )

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    _otel_initialized = True


