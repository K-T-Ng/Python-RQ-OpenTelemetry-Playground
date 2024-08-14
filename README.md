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

## Dependencies Version
* Docker Version: 24.0.7
* Docker Compose Plugin Version: v2.29.1-desktop.1

## Getting Started
1. Spin up monitor stack.
    ```bash
    docker compose up -d
    ```

    The stack contains the following components and expose folloing ports
    | Container | Ports | Remark |
    |-----------|-------|--------|
    | Grafana | 3000 | `admin:CHANGEME`. Change it if you want |
    | Prometheus | 9090 | Not in use |
    | ElasticSearch | 9200 | `elastic:CHANGEME`. Change it if you want |
    | Jaeger Collector | 14269 |  |
    | Jaeger Query | 16686, 16687 | 16686 for Jaeger Query UI |
    | OpenTelemetry Collector | 4317, 4318 | |
    | Redis | 6379 | |

2. Install pre-requisite python packages
    ```bash
    pip install -r requirements.txt
    ```

3. Launch producer and worker in different terminal
    ```bash
    # In terminal A
    python -m src.produer

    # In terminal B
    python -m src.worker
    ```

4. Login Grafana and Check dashabord.
    * You can open Grafana via `http://localhost:3000` in browser.
    * Access dashboard via `Home -> Dashboards -> Dashbaords -> RQ Instrumentation Playground`
    * Click one of the Trace ID, then the logs and trace detail for the given trace id will appear.
5. To clean all the stuffs...
    * Shut down producer and worker. `Ctrl+C` on those terminal in steps 3.
    * Shut down monitor stack by `docker compose down --remove-orphans`
