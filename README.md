# Python RQ OpenTelemetry Playground
## Overview
### Goal
A playground for trying to instrument logs, metrics and tracing signals via [OpenTelemetry](https://opentelemetry.io/) for [Python RQ](https://github.com/rq/rq) library.

- [ ] Write a small instrumentation library by referencing instrumentation libraries from [opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-celery)
- [x] Configure following components to bring telemetry data to different storage backend and present it.
    - OpenTelemetry collector
    - Jaeger Collector
    - Prometheus
    - ElasticSearch
    - Jaeger Query
    - Grafana
- [ ] Create an example to cover as many usage as possible for Python RQ and see whether it works

### Motivation
Have this need on work.

## Getting Started
### Launch Monitor Stack
```
docker compose up -d
```
