import pytest
import requests
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sre_metrics import instrument_fastapi

@pytest.fixture
def fastapi_app():
    """Create an instrumented FastAPI app for testing"""
    app = FastAPI()
    
    @app.get("/")
    def read_root():        return {"Hello": "World"}
    
    @app.get("/error")
    def trigger_error():
        raise HTTPException(status_code=404, detail="Not found")
    
    # Instrument with default port 9090
    instrument_fastapi(app)
    return app

def test_fastapi_metrics_collection(fastapi_app):
    client = TestClient(fastapi_app)
    
    # Make requests to generate metrics
    client.get("/")
    response = client.get("/error")
    assert response.status_code == 404  # Verify the error endpoint
    
    # Verify metrics on port 9090
    metrics = requests.get("http://localhost:9090/metrics").text
    
    # Check individual status codes
    assert 'http_requests_total{method="GET",path="/",status_code="200"}' in metrics
    assert 'http_requests_total{method="GET",path="/error",status_code="404"}' in metrics
    
    # Check latency metrics
    assert 'http_request_duration_seconds_bucket{le="0.01"' in metrics
    assert 'http_request_duration_seconds_count{method="GET",path="/"}' in metrics
    
    # Check in-progress gauge
    assert 'http_in_progress_requests 0.0' in metrics