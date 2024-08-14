"""Initalize OpenTelemetry instrumentation for logs/metrics/logs"""

import logging
from typing import List, Tuple

from opentelemetry import _logs, metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.rq import RQInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    MetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def init_traces(
    resource: Resource, otlp_http_endpoint: str, enable_console_exporter: bool = False
):
    """Initalize traces instrumentation"""
    provider = TracerProvider(resource=resource)

    if enable_console_exporter:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

    otlp_exporter = OTLPSpanExporter(endpoint=f"{otlp_http_endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)


def init_meter(
    resource: Resource, otlp_http_endpoint: str, enable_console_exporter: bool = False
):
    """Initialize metric instrumentation"""
    metric_readers: List[MetricReader] = []

    if enable_console_exporter:
        console_exporter = ConsoleMetricExporter()
        metric_readers.append(PeriodicExportingMetricReader(console_exporter))

    oltp_exporter = OTLPMetricExporter(endpoint=f"{otlp_http_endpoint}/v1/metrics")
    metric_readers.append(PeriodicExportingMetricReader(oltp_exporter))

    provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    metrics.set_meter_provider(provider)


def init_logs(
    resource: Resource,
    otlp_http_endpoint: str,
    logger_names: Tuple[str],
    enable_console_exporter: bool = False,
):
    """Initialize logs instrumentation"""
    provider = LoggerProvider(resource=resource)

    if enable_console_exporter:
        console_exporter = ConsoleLogExporter()
        provider.add_log_record_processor(BatchLogRecordProcessor(console_exporter))

    otlp_exporter = OTLPLogExporter(endpoint=f"{otlp_http_endpoint}/v1/logs")
    provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

    _logs.set_logger_provider(provider)

    handler = LoggingHandler(level=logging.NOTSET, logger_provider=provider)
    for logger_name in logger_names:
        logging.getLogger(logger_name).addHandler(handler)


def initialize(
    otlp_http_endpoint: str,
    logger_names: Tuple[str],
    enable_console_exporter: bool = False,
):
    """Initalize OpenTelemetry instrumentation"""
    resource = Resource(
        attributes={
            "service.name": "rq-instrumentation-playground",
            "service.version": "0.1.0",
        }
    )
    init_logs(resource, otlp_http_endpoint, logger_names, enable_console_exporter)
    init_meter(resource, otlp_http_endpoint, enable_console_exporter)
    init_traces(resource, otlp_http_endpoint, enable_console_exporter)
    RQInstrumentor().instrument()
