"""OpenTelemetry configuration for the project."""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased


def setup_telemetry(service_name: str) -> None:
    """Configure OpenTelemetry tracing.

    Parameters
    ----------
    service_name:
        Identifier for this service emitted in the trace resource.
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    resource = Resource(attributes={"service.name": service_name})
    provider = TracerProvider(
        sampler=ParentBased(TraceIdRatioBased(0.1)),
        resource=resource,
    )
    exporter_kwargs = {}
    if endpoint:
        exporter_kwargs["endpoint"] = endpoint
    span_exporter = OTLPSpanExporter(**exporter_kwargs)
    provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(provider)


__all__ = ["setup_telemetry"]