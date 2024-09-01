"""Utils for supporting PoC RQ instrumentation library"""

import logging
from typing import Optional, Tuple

from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker

from opentelemetry.sdk._logs import LoggingHandler


def _extract_attributes(
    job: Optional[Job] = None,
    queue: Optional[Queue] = None,
    worker: Optional[Worker] = None,
):
    """Extract attributes for instrumentation from job, queue and worker
    Skip corresponding attributes if not provided
    """
    attributes = {}

    if job:
        attributes["job.id"] = job.id
        attributes["job.func_name"] = job.func_name

    if queue:
        attributes["queue.name"] = queue.name

    if worker:
        attributes["worker.name"] = worker.name

    return attributes


def _add_handler_with_provider_to_logger(
    logger_names: Tuple[str], handler: LoggingHandler
):
    for name in logger_names:
        logging.getLogger(name).addHandler(handler)


def _remove_handler_with_provider_from_logger(
    logger_names: Tuple[str], handler: LoggingHandler
):
    for name in logger_names:
        logging.getLogger(name).removeHandler(handler)
