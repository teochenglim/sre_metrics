from fastapi import Request
from prometheus_client import start_http_server
from .core import SREMetricsCore
import time
from typing import Optional, Dict, List, Callable, Union

def instrument_fastapi(
    app,
    metrics_port: int = 9090,
    prefix: str = "http_",
    buckets: List[float] = [0.01, 0.05, 0.1, 0.5, 1, 5],
    excluded_paths: Optional[List[str]] = None,
    group_status_codes: bool = True,
    inprogress_labels: bool = False,
    custom_labels: Optional[Dict[str, str]] = None,
    skip_untemplated: bool = False
):
    core = SREMetricsCore(
        prefix=prefix,
        excluded_paths=excluded_paths,
        buckets=tuple(buckets),
        group_status_codes=group_status_codes,
        inprogress_labels=inprogress_labels,
        custom_labels=custom_labels,
        skip_untemplated=skip_untemplated
    )
    
    start_http_server(metrics_port)
    
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        path = request.url.path
        method = request.method
        
        if path == '/metrics' or core._should_exclude(path):
            return await call_next(request)
        
        # Check if route has path parameters
        has_template = bool(
            request.scope.get("route") and 
            any(param in request.scope["route"].path 
                for param in ["{", "<"])
        )
        
        # Handle in-progress metrics
        if core.inprogress_labels:
            core.in_progress.labels(method=method, path=path).inc()
        else:
            core.in_progress.inc()
            
        start = time.time()
        
        try:
            response = await call_next(request)
            core.record_metrics(
                method=method,
                path=path,
                status_code=response.status_code,
                duration=time.time() - start,
                has_template=has_template
            )
            return response
        finally:
            if core.inprogress_labels:
                core.in_progress.labels(method=method, path=path).dec()
            else:
                core.in_progress.dec()
    
    return app