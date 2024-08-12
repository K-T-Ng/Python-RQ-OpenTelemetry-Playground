"""Utils for supporting PoC RQ instrumentation library"""

from opentelemetry import trace


def _trace_enqueue_call(func, instance, args, kwargs):
    tracer = trace.get_tracer(__name__)
    print(tracer)
    with tracer.start_as_current_span(
        name="enqueue_call", kind=trace.SpanKind.PRODUCER
    ) as span:
        print(span)
        response = func(*args, **kwargs)

    return response
