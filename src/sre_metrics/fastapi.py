from fastapi import Request
from prometheus_client import start_http_server
from .core import SREMetricsCore
import time

class FastAPIMetrics:
    def __init__(self, app, metrics_port: int = 9090, **kwargs):
        self.core = SREMetricsCore(**kwargs)
        start_http_server(metrics_port)
        app.middleware('http')(self.middleware)

    async def middleware(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        if path == '/metrics' or self.core._should_exclude(path):
            return await call_next(request)
        
        self.core.in_progress.inc()
        start = time.time()
        
        try:
            response = await call_next(request)
            self.core.record_metrics(method, path, response.status_code, time.time() - start)
            return response
        finally:
            self.core.in_progress.dec()

def instrument_fastapi(app, **kwargs):
    """Public interface for FastAPI instrumentation"""
    return FastAPIMetrics(app, **kwargs)