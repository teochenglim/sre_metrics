from prometheus_client import Counter, Histogram, Gauge
import re
from typing import Optional, List, Tuple, Dict, Callable, Union
import os

class SREMetricsCore:
    def __init__(
        self,
        prefix: str = "http_",
        excluded_paths: Optional[List[str]] = None,
        buckets: Tuple[float, ...] = (0.01, 0.05, 0.1, 0.5, 1, 5),
        group_status_codes: bool = True,
        inprogress_labels: bool = False,
        custom_labels: Optional[Dict[str, str]] = None,
        skip_untemplated: bool = False,
        normalize_path: Optional[Callable[[str], str]] = None,
        enable_by_envvar: Optional[str] = None
    ):
        if enable_by_envvar and not os.getenv(enable_by_envvar):
            self.disabled = True
            return
        self.disabled = False
        
        self.excluded_paths = [re.compile(p) for p in excluded_paths] if excluded_paths else []
        self.group_status_codes = group_status_codes
        self.inprogress_labels = inprogress_labels
        self.normalize_path = normalize_path
        self.skip_untemplated = skip_untemplated
        self.custom_labels = custom_labels or {}
        
        # Common label names
        labels = ['method', 'path']
        inprogress_labelnames = labels.copy() if inprogress_labels else []
        
        # Rate metrics
        self.requests = Counter(
            f'{prefix}requests_total',
            'Total requests',
            labels + ['status_code']
        )
        
        if group_status_codes:
            self.requests_grouped = Counter(
                f'{prefix}requests_by_class_total',
                'Total requests by status class',
                labels + ['status_class']
            )
        
        # Error metrics
        self.errors = Counter(
            f'{prefix}errors_total',
            'Total errors',
            labels + ['error_class']
        )
        
        # Duration metrics
        self.latency = Histogram(
            f'{prefix}request_duration_seconds',
            'Request duration',
            labels,
            buckets=buckets
        )
        
        # Saturation metric
        self.in_progress = Gauge(
            f'{prefix}in_progress_requests',
            'In-progress requests',
            inprogress_labelnames
        )

    def _should_exclude(self, path: str) -> bool:
        if self.disabled:
            return True
        return any(p.fullmatch(path) for p in self.excluded_paths)

    def _classify_status(self, status_code: int) -> str:
        return f"{status_code // 100}xx"

    def _prepare_path(self, path: str, has_template: bool) -> Optional[str]:
        if self.skip_untemplated and not has_template:
            return None
        if self.normalize_path:
            return self.normalize_path(path)
        return path

    def record_metrics(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        has_template: bool = True
    ):
        if self.disabled or self._should_exclude(path):
            return
            
        path = self._prepare_path(path, has_template)
        if path is None:
            return
            
        labels = {
            'method': method,
            'path': path,
            **self.custom_labels
        }
        
        # Track requests
        self.requests.labels(**labels, status_code=str(status_code)).inc()
        
        if self.group_status_codes:
            self.requests_grouped.labels(**labels, status_class=self._classify_status(status_code)).inc()
        
        # Track errors
        if status_code >= 400:
            self.errors.labels(**labels, error_class=self._classify_status(status_code)).inc()
        
        # Track latency
        self.latency.labels(**labels).observe(duration)