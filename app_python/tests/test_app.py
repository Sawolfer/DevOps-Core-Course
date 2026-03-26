"""
Unit tests for DevOps Info Service FastAPI application.
"""
import re
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

client = TestClient(app)

class TestRootEndpoint:
    """Test suite for the root endpoint (/)."""
    
    def test_root_status_code(self):
        """Test that root endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_response_structure(self):
        """Test that root endpoint returns all required sections."""
        response = client.get("/")
        data = response.json()
        
        assert "service" in data
        assert "system" in data
        assert "runtime" in data
        assert "request" in data
        assert "endpoints" in data
    
    def test_service_info(self):
        """Test service information structure and values."""
        response = client.get("/")
        service = response.json()["service"]
        
        assert service["name"] == "devops-info-service"
        assert service["version"] == "1.0.0"
        assert service["framework"] == "FastAPI"
        assert "description" in service
    
    def test_system_info(self):
        """Test system information structure."""
        response = client.get("/")
        system = response.json()["system"]
        
        assert "hostname" in system
        assert "platform" in system
        assert "architecture" in system
        assert "python_version" in system
        
        assert system["hostname"].strip() != ""
    
    def test_runtime_info(self):
        """Test runtime information structure."""
        response = client.get("/")
        runtime = response.json()["runtime"]
        
        
        assert "uptime_seconds" in runtime
        assert "uptime_human" in runtime
        assert "current_time" in runtime
        assert "timezone" in runtime
        
        assert runtime["uptime_seconds"] >= 0

        current_time = runtime["current_time"]
        assert current_time.endswith("Z")
        assert len(current_time) > 20
    
    def test_request_info(self):
        """Test request information capture."""
        headers = {"user-agent": "pytest-client/1.0"}
        response = client.get("/", headers=headers)
        request_info = response.json()["request"]
        
        assert "client_ip" in request_info
        assert request_info["user_agent"] == "pytest-client/1.0"
        assert request_info["method"] == "GET"
        assert request_info["path"] == "/"
    
    def test_endpoints_listing(self):
        """Test that endpoints are properly listed."""
        response = client.get("/")
        endpoints = response.json()["endpoints"]
        
        assert len(endpoints) >= 2

        root_endpoint = next((e for e in endpoints if e["path"] == "/"), None)
        assert root_endpoint is not None
        assert root_endpoint["method"] == "GET"
        
        health_endpoint = next((e for e in endpoints if e["path"] == "/health"), None)
        assert health_endpoint is not None
        assert health_endpoint["method"] == "GET"

class TestHealthEndpoint:
    """Test suite for the health check endpoint (/health)."""
    
    def test_health_status_code(self):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_response_structure(self):
        """Test health endpoint response structure."""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
    
    def test_health_status_value(self):
        """Test that health status is 'healthy'."""
        response = client.get("/health")
        assert response.json()["status"] == "healthy"
    
    def test_health_timestamp_format(self):
        """Test that timestamp is in correct ISO format."""
        response = client.get("/health")
        timestamp = response.json()["timestamp"]
        
        assert timestamp.endswith("Z")
        assert len(timestamp) > 20

class TestErrorHandling:
    """Test suite for error handling."""
    
    def test_404_not_found(self):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"] == "Not Found"
        assert "message" in data
    
    def test_invalid_method(self):
        """Test invalid HTTP method."""
        response = client.post("/")
        assert response.status_code == 405 

class TestUptimeCalculation:
    """Test suite for uptime calculation."""
    
    def test_uptime_consistency(self):
        """Test that uptime is consistent across endpoints."""
        response_root = client.get("/")
        response_health = client.get("/health")
        
        root_uptime = response_root.json()["runtime"]["uptime_seconds"]
        health_uptime = response_health.json()["uptime_seconds"]
        
        assert abs(root_uptime - health_uptime) <= 1
    
    def test_uptime_human_format(self):
        """Test human-readable uptime format."""
        response = client.get("/")
        uptime_human = response.json()["runtime"]["uptime_human"]
        
        # Should contain hours and minutes
        assert "hours" in uptime_human
        assert "minutes" in uptime_human


class TestPrometheusMetrics:
    """Test suite for Prometheus metrics endpoint (/metrics)."""

    def test_metrics_endpoint_exposes_metrics(self):
        client.get("/")
        client.get("/health")

        response = client.get("/metrics")
        assert response.status_code == 200

        content_type = response.headers.get("content-type", "")
        assert "text/plain" in content_type

        body = response.text
        assert "http_requests_total" in body
        assert "http_request_duration_seconds" in body
        assert "http_active_requests" in body

        assert re.search(
            r'http_requests_total\{[^}]*endpoint="/"[^}]*method="GET"[^}]*status_code="200"[^}]*\}',
            body,
        )
        assert "devops_info_endpoint_calls_total" in body
        assert 'devops_info_endpoint_calls_total{endpoint="/"}' in body
        assert "devops_info_system_collection_seconds" in body
        assert "devops_info_uptime_seconds" in body

if __name__ == "__main__":
    pytest.main(["-v", "--cov=.", "--cov-report=term-missing"])