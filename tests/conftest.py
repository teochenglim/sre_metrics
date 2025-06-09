import pytest
from prometheus_client.registry import REGISTRY

@pytest.fixture(autouse=True)
def clear_prometheus_registry():
    """Clear Prometheus registry between tests"""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)