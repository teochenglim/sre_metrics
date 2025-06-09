import requests
from flask import Flask
from sre_metrics import instrument_flask

def test_flask_metrics():
    """Test basic Flask metric collection"""
    app = Flask(__name__)
    
    @app.route("/")
    def root():
        return "Hello"
    
    @app.route("/error")
    def error():
        return "Not Found", 404
    
    # Instrument with default port 9090
    instrument_flask(app, metrics_port=9091)
    
    client = app.test_client()
    client.get("/")
    client.get("/error")
    
    # Verify metrics endpoint
    metrics = requests.get("http://localhost:9091/metrics").text
    
    # Check individual status codes
    assert 'http_requests_total{method="GET",path="/",status_code="200"}' in metrics
    assert 'http_requests_total{method="GET",path="/error",status_code="404"}' in metrics
    
    # Check latency metrics
    assert 'http_request_duration_seconds_bucket{le="0.01"' in metrics
    assert 'http_request_duration_seconds_count{method="GET",path="/"}' in metrics
    
    # Check in-progress gauge
    assert 'http_in_progress_requests 0.0' in metrics