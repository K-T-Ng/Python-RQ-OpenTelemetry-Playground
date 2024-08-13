"""Initalize OpenTelemetry instrumentation for logs/metrics/logs"""

import logging

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from opentelemetry import _logs, metrics, trace


def init_traces(resource: Resource):
    """Initalize traces instrumentation"""
    provider = TracerProvider(resource=resource)

    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))

    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)


def init_meter(resource: Resource):
    """Initialize metric instrumentation"""
    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(provider)


def init_logs(resource: Resource):
    """Initialize logs instrumentation"""
    provider = LoggerProvider(resource=resource)
    processor = BatchLogRecordProcessor(ConsoleLogExporter())
    provider.add_log_record_processor(processor)
    _logs.set_logger_provider(provider)


def get_logger():
    """Get logger (logging.getLogger(__name__)) with logs provider injected as handler"""
    logger = logging.getLogger(__name__)
    provier = _logs.get_logger_provider()
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=provier)
    logger.addHandler(handler)
    return logger


def init_otel():
    """Initalize OpenTelemetry instrumentation"""
    resource = Resource(
        attributes={
            "service.name": "rq-instrumentation-playground",
            "service.version": "0.1.0",
        }
    )
    init_logs(resource)
    init_meter(resource)
    init_traces(resource)
