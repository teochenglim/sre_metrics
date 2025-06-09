from flask import request, Response
from prometheus_client import start_http_server
from .core import SREMetricsCore
import time

class FlaskMetrics:
    def __init__(self, app, metrics_port: int = 9090, **kwargs):
        self.core = SREMetricsCore(**kwargs)
        start_http_server(metrics_port)
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        if request.path == '/metrics' or self.core._should_exclude(request.path):
            return
        self.core.in_progress.inc()
        request.start_time = time.time()

    def after_request(self, response: Response):
        if request.path == '/metrics' or self.core._should_exclude(request.path):
            return response
            
        self.core.record_metrics(
            request.method,
            request.path,
            response.status_code,
            time.time() - request.start_time
        )
        self.core.in_progress.dec()
        return response

def instrument_flask(app, **kwargs):
    """Public interface for Flask instrumentation"""
    return FlaskMetrics(app, **kwargs)