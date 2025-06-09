from prometheus_client import Counter, Histogram, Gauge
import re
from typing import Optional, List, Tuple

class SREMetricsCore:
    def __init__(
        self,
        prefix: str = "http_",
        excluded_paths: Optional[List[str]] = None,
        buckets: Tuple[float, ...] = (0.01, 0.05, 0.1, 0.5, 1, 5),
        group_status_codes: bool = True
    ):
        self.excluded_paths = [re.compile(p) for p in excluded_paths] if excluded_paths else []
        self.group_status_codes = group_status_codes
        
        # Rate (individual status codes)
        self.requests = Counter(
            f'{prefix}requests_total',
            'Total requests',
            ['method', 'path', 'status_code']
        )
        
        # Rate (grouped status classes)
        if group_status_codes:
            self.requests_grouped = Counter(
                f'{prefix}requests_by_class_total',
                'Total requests by status class',
                ['method', 'path', 'status_class']
            )
        
        # Errors
        self.errors = Counter(
            f'{prefix}errors_total',
            'Total errors',
            ['method', 'path', 'error_class']
        )
        
        # Duration
        self.latency = Histogram(
            f'{prefix}request_duration_seconds',
            'Request duration',
            ['method', 'path'],
            buckets=buckets
        )
        
        # Saturation
        self.in_progress = Gauge(
            f'{prefix}in_progress_requests',
            'In-progress requests'
        )

    def _should_exclude(self, path: str) -> bool:
        return any(p.fullmatch(path) for p in self.excluded_paths)

    def _classify_status(self, status_code: int) -> str:
        return f"{status_code // 100}xx"

    def record_metrics(self, method: str, path: str, status_code: int, duration: float):
        """Core metrics recording logic"""
        if self._should_exclude(path):
            return
            
        # Always track individual status codes
        self.requests.labels(method, path, str(status_code)).inc()
        
        # Track grouped if enabled
        if self.group_status_codes:
            self.requests_grouped.labels(method, path, self._classify_status(status_code)).inc()
        
        # Track errors
        if status_code >= 400:
            self.errors.labels(method, path, self._classify_status(status_code)).inc()
        
        # Track latency
        self.latency.labels(method, path).observe(duration)