# SRE Metrics

[![PyPI](https://img.shields.io/pypi/v/sre-metrics)](https://pypi.org/project/sre-metrics/)

Minimalist SRE metrics for Python web frameworks.

## Features

- Default metrics on port 9090
- Tracks individual status codes + optional grouping
- FastAPI and Flask support
- <5ms overhead

## FastAPI Installation

```bash
pip install sre-metrics[fastapi]

```

### FastAPI Usage

```python
from fastapi import FastAPI
from sre-metrics import instrument_fastapi

app = FastAPI()
instrument_fastapi(app)  # Metrics on :9090 by default

# Custom port
instrument_fastapi(app, metrics_port=9091, excluded_paths=["/healthz"])

```


### Flask Installation

```bash
pip install sre-metrics[flask]
```

```python
from flask import Flask
from sre-metrics import instrument_flask

app = Flask(__name__)
instrument_flask(app)  # Metrics on :9090

# Custom options:
instrument_flask(app, metrics_port=9091, excluded_paths=["/healthz"])

```

## Rebuild locally

```bash
uv sync
uv run pytest
rm -rf build/ dist/ sre_metrics.egg-info/
uv run python -m build
pip install --force-reinstall dist/sre_metrics-1.0.0-py3-none-any.whl
python -c "import sre_metrics;"

## twine
uv add twine
twine upload dist/*
```