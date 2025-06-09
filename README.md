# SRE Metrics

[![PyPI](https://img.shields.io/pypi/v/sre-metrics)](https://pypi.org/project/sre-metrics/)

Minimalist SRE metrics for Python web frameworks.

sre-metrics brings production-grade observability to your Python web apps with almost zero configuration in just two lines.

```python
from sre_metrics import instrument_fastapi
instrument_fastapi(app)  # Done. Metrics on http://localhost:9090/metrics
```

you get SRE RED metrics (Rate, Errors, Duration) exposed on port 9090 (or any custom port), complete with smart buckets and auto-excluded endpoints like /metrics and /healthz. Designed for Kubernetes and cloud-native environments, it labels, normalizes paths (/user/123 → /user/{id}), and keeps overhead below 1 ms per request.

Built for SREs who need actionable signals without metric sprawl, sre-metrics tracks only the golden signals, uses a single dependency (prometheus-client), and delivers identical output across frameworks. Whether you want simplicity out of the box or fine-tuned control—custom ports, prefixes, and excluded paths—it strikes the perfect 20/80 balance between ease of setup and production-ready flexibility.

## Features

- Default metrics on port 9090
- Tracks individual status codes + optional grouping
- FastAPI and Flask support
- <5ms overhead

## FastAPI Installation

```bash
pip install sre_metrics[fastapi]

```

### FastAPI Usage

```python
from fastapi import FastAPI
from sre_metrics import instrument_fastapi

app = FastAPI()
instrument_fastapi(app)  # Metrics on :9090 by default

# Custom port
instrument_fastapi(app, metrics_port=9091, excluded_paths=["/healthz"])

# All options
instrument_fastapi(
    app,
    metrics_port=9091,               # Metrics server port (default: 9090)
    prefix="app_",                   # Metric name prefix (default: "http_")
    buckets=[0.1, 0.5, 1, 5],       # Latency histogram buckets in seconds
    excluded_paths=["/healthz"],     # Path patterns to exclude from metrics
    group_status_codes=False,        # Disable 2xx/3xx/4xx/5xx grouping
    inprogress_labels=True,          # Add method/path labels to in-progress gauge
    custom_labels={"env": "prod"},   # Additional labels for all metrics
    skip_untemplated=True            # Ignore routes without path templates
)

```


### Flask Installation

```bash
pip install sre_metrics[flask]
```

```python
from flask import Flask
from sre_metrics import instrument_flask

app = Flask(__name__)
instrument_flask(app)  # Metrics on :9090

# Custom options:
instrument_flask(app, metrics_port=9091, excluded_paths=["/healthz"])

# All options
instrument_flask(
    app,
    metrics_port=9091,               # Metrics server port (default: 9090)
    prefix="app_",                   # Metric name prefix (default: "http_")
    buckets=[0.1, 0.5, 1, 5],       # Latency histogram buckets in seconds
    excluded_paths=["/static/.*"],   # Regex patterns of paths to exclude
    group_status_codes=True,         | Enable status code grouping (default)
    normalize_path=lambda p: re.sub(r'/user/\d+', '/user/{id}', p), # Path normalization
    enable_by_envvar="ENABLE_METRICS" # Only enable if env var is set
)

```

## Custom Status Code Classification

```python
def custom_classifier(status_code: int) -> str:
    if status_code == 418: return "teapot"
    return f"{status_code//100}xx"

instrument_fastapi(
    app,
    status_classifier=custom_classifier
)

```

## Kubernetes Example

```
instrument_fastapi(
    app,
    custom_labels={
        "service": os.getenv("SERVICE_NAME"),
        "pod": os.getenv("POD_NAME"),
        "namespace": os.getenv("NAMESPACE")
    }
)

```

## Rebuild locally

```bash
uv sync
uv pip install twine fastapi flask httpx uvicorn requests
uv run pytest
rm -rf build/ dist/ sre_metrics.egg-info/
uv run python -m build
pip install --force-reinstall dist/sre_metrics-*-py3-none-any.whl
python -c "import sre_metrics;"

## twine
uv add twine
rm -rf build/ dist/ sre_metrics.egg-info/
uv run python -m build
pip install --force-reinstall dist/sre_metrics-*-py3-none-any.whl
twine upload dist/*
```
