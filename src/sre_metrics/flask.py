from flask import request, Response
from prometheus_client import start_http_server
from .core import SREMetricsCore
import time
import re
from typing import Optional, List, Dict, Callable, Union

def instrument_flask(
    app,
    metrics_port: int = 9090,
    prefix: str = "http_",
    buckets: List[float] = [0.01, 0.05, 0.1, 0.5, 1, 5],
    excluded_paths: Optional[List[str]] = None,
    group_status_codes: bool = True,
    normalize_path: Optional[Callable[[str], str]] = None,
    enable_by_envvar: Optional[str] = None
):
    core = SREMetricsCore(
        prefix=prefix,
        excluded_paths=excluded_paths,
        buckets=tuple(buckets),
        group_status_codes=group_status_codes,
        normalize_path=normalize_path,
        enable_by_envvar=enable_by_envvar
    )
    
    start_http_server(metrics_port)
    
    @app.before_request
    def before_request():
        if request.path == '/metrics' or core._should_exclude(request.path):
            return
        core.in_progress.inc()
        request.start_time = time.time()

    @app.after_request
    def after_request(response: Response):
        if request.path == '/metrics' or core._should_exclude(request.path):
            return response
            
        path = request.path
        if core.normalize_path:
            path = core.normalize_path(path)
            
        core.record_metrics(
            method=request.method,
            path=path,
            status_code=response.status_code,
            duration=time.time() - request.start_time
        )
        core.in_progress.dec()
        return response
    
    return app