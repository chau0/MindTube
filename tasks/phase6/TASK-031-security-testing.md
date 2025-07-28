# TASK-031: Security Testing

## Task Information
- **ID**: TASK-031
- **Phase**: 6 - Testing & Quality Assurance
- **Estimate**: 60 minutes
- **Dependencies**: TASK-030
- **Status**: 🔴 Backlog

## Description
Implement comprehensive security validation and testing to ensure the application is protected against common vulnerabilities and follows security best practices.

## Acceptance Criteria
- [ ] Test input validation and sanitization
- [ ] Test authentication and authorization mechanisms
- [ ] Test rate limiting effectiveness
- [ ] Validate secure credential handling
- [ ] Test for common web vulnerabilities (OWASP Top 10)
- [ ] Add automated security scanning
- [ ] Document security measures and compliance

## Implementation Details

### Security Test Categories

#### 1. Input Validation Security
```python
# tests/security/test_input_validation.py
import pytest
from mindtube.api.app import app
from fastapi.testclient import TestClient

class TestInputValidation:
    
    def setup_method(self):
        self.client = TestClient(app)
    
    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test protection against SQL injection attempts"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; SELECT * FROM config; --",
            "admin'--",
            "' UNION SELECT password FROM users--"
        ]
        
        for payload in malicious_inputs:
            response = self.client.post("/analyze", json={
                "url": f"https://youtu.be/{payload}",
                "options": {"include_summary": True}
            })
            
            # Should either reject with 400 or handle safely
            assert response.status_code in [400, 422], f"Payload '{payload}' not properly handled"
            if response.status_code == 400:
                assert "invalid" in response.json().get("detail", "").lower()
    
    @pytest.mark.security
    def test_xss_prevention(self):
        """Test protection against XSS attacks"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
            "<svg onload=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            response = self.client.post("/analyze", json={
                "url": f"https://youtu.be/test",
                "title": payload,
                "options": {"include_summary": True}
            })
            
            if response.status_code == 200:
                # Check that payload is properly escaped in response
                response_text = response.text
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
                assert "onerror=" not in response_text
    
    @pytest.mark.security
    def test_path_traversal_prevention(self):
        """Test protection against path traversal attacks"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        for payload in traversal_payloads:
            # Test file operations that might be vulnerable
            response = self.client.get(f"/artifacts/{payload}")
            assert response.status_code in [400, 404, 403], f"Path traversal not prevented: {payload}"
```

#### 2. Authentication & Authorization
```python
# tests/security/test_auth_security.py
class TestAuthSecurity:
    
    @pytest.mark.security
    def test_api_key_validation(self):
        """Test API key validation and security"""
        client = TestClient(app)
        
        # Test without API key
        response = client.post("/analyze", json={"url": "https://youtu.be/test"})
        # Should work for public endpoints or require auth appropriately
        
        # Test with invalid API key
        headers = {"Authorization": "Bearer invalid_key_123"}
        response = client.post("/analyze", json={"url": "https://youtu.be/test"}, headers=headers)
        
        if app.config.get("require_auth"):
            assert response.status_code == 401
    
    @pytest.mark.security
    def test_rate_limiting_bypass_attempts(self):
        """Test that rate limiting cannot be easily bypassed"""
        client = TestClient(app)
        
        # Attempt to bypass with different headers
        bypass_headers = [
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Real-IP": "127.0.0.1"},
            {"X-Originating-IP": "127.0.0.1"},
            {"User-Agent": "Different-Agent"},
        ]
        
        # Make requests rapidly
        for headers in bypass_headers:
            responses = []
            for _ in range(20):  # Exceed rate limit
                response = client.post("/analyze", 
                                     json={"url": "https://youtu.be/test"}, 
                                     headers=headers)
                responses.append(response.status_code)
            
            # Should eventually hit rate limit
            rate_limited = any(status == 429 for status in responses)
            assert rate_limited, f"Rate limiting bypassed with headers: {headers}"
```

#### 3. Credential Security
```python
# tests/security/test_credential_security.py
class TestCredentialSecurity:
    
    @pytest.mark.security
    def test_environment_variable_exposure(self):
        """Test that sensitive environment variables are not exposed"""
        client = TestClient(app)
        
        # Test debug endpoints don't expose secrets
        response = client.get("/debug/env")
        if response.status_code == 200:
            env_data = response.json()
            sensitive_keys = [
                "AZURE_OPENAI_API_KEY",
                "DATABASE_PASSWORD", 
                "SECRET_KEY",
                "JWT_SECRET"
            ]
            
            for key in sensitive_keys:
                assert key not in env_data, f"Sensitive key {key} exposed in debug endpoint"
    
    @pytest.mark.security
    def test_api_key_in_logs(self):
        """Test that API keys are not logged"""
        import logging
        from io import StringIO
        
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logging.getLogger().addHandler(handler)
        
        # Make request with API key
        client = TestClient(app)
        headers = {"Authorization": "Bearer test_api_key_12345"}
        client.post("/analyze", json={"url": "https://youtu.be/test"}, headers=headers)
        
        log_contents = log_capture.getvalue()
        assert "test_api_key_12345" not in log_contents, "API key found in logs"
        
        logging.getLogger().removeHandler(handler)
```

#### 4. Common Vulnerability Tests
```python
# tests/security/test_common_vulnerabilities.py
class TestCommonVulnerabilities:
    
    @pytest.mark.security
    def test_cors_configuration(self):
        """Test CORS configuration is secure"""
        client = TestClient(app)
        
        # Test with malicious origin
        headers = {"Origin": "https://evil.com"}
        response = client.options("/analyze", headers=headers)
        
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        if cors_header:
            assert cors_header != "*", "CORS allows all origins"
            assert "evil.com" not in cors_header, "CORS allows malicious origin"
    
    @pytest.mark.security
    def test_security_headers(self):
        """Test that security headers are present"""
        client = TestClient(app)
        response = client.get("/")
        
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=",
        }
        
        for header, expected in security_headers.items():
            header_value = response.headers.get(header)
            if isinstance(expected, list):
                assert header_value in expected, f"Security header {header} missing or incorrect"
            else:
                assert header_value and expected in header_value, f"Security header {header} missing or incorrect"
    
    @pytest.mark.security
    def test_information_disclosure(self):
        """Test for information disclosure vulnerabilities"""
        client = TestClient(app)
        
        # Test error responses don't leak sensitive info
        response = client.post("/analyze", json={"invalid": "data"})
        
        if response.status_code >= 400:
            error_text = response.text.lower()
            sensitive_patterns = [
                "traceback",
                "stack trace",
                "file not found",
                "permission denied",
                "database error",
                "internal server error"
            ]
            
            for pattern in sensitive_patterns:
                assert pattern not in error_text, f"Error response contains sensitive info: {pattern}"
```

### Automated Security Scanning

#### Security Scan Configuration
```python
# tests/security/test_automated_scanning.py
import subprocess
import json

class TestAutomatedScanning:
    
    @pytest.mark.security
    @pytest.mark.slow
    def test_dependency_vulnerabilities(self):
        """Test for known vulnerabilities in dependencies"""
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            vulnerabilities = json.loads(result.stdout)
            high_severity = [v for v in vulnerabilities if v.get("severity") == "high"]
            assert len(high_severity) == 0, f"High severity vulnerabilities found: {high_severity}"
    
    @pytest.mark.security
    def test_secrets_in_code(self):
        """Test for hardcoded secrets in codebase"""
        result = subprocess.run(
            ["truffleHog", "--regex", "--entropy=False", "."],
            capture_output=True,
            text=True
        )
        
        # Check for common secret patterns
        secret_patterns = [
            "api_key",
            "password",
            "secret",
            "token"
        ]
        
        if result.stdout:
            for pattern in secret_patterns:
                assert pattern not in result.stdout.lower(), f"Potential secret found: {pattern}"
```

### Security Configuration

#### Security Settings
```python
# mindtube/core/security.py
from typing import List
import secrets

class SecurityConfig:
    """Security configuration and utilities"""
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    
    # Input validation
    MAX_URL_LENGTH = 2048
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", "\"", "'", "&", ";"]
        for char in dangerous_chars:
            text = text.replace(char, "")
        return text.strip()
```

### CI Security Pipeline

#### Security Testing Workflow
```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install security tools
      run: |
        pip install safety bandit semgrep
        npm install -g @microsoft/rush
    
    - name: Run dependency security check
      run: safety check --json
    
    - name: Run static security analysis
      run: bandit -r mindtube/ -f json
    
    - name: Run semgrep security rules
      run: semgrep --config=auto mindtube/
    
    - name: Run security tests
      run: pytest tests/security -m security -v
    
    - name: Upload security results
      uses: actions/upload-artifact@v3
      with:
        name: security-results
        path: security-reports/
```

## Security Documentation

### Security Checklist
- [ ] Input validation implemented
- [ ] Authentication mechanisms tested
- [ ] Rate limiting configured
- [ ] Security headers implemented
- [ ] Dependency vulnerabilities checked
- [ ] Secrets management verified
- [ ] Error handling secure
- [ ] Logging doesn't expose sensitive data

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Security tests pass consistently
- [ ] Automated security scanning integrated
- [ ] Security documentation updated
- [ ] Vulnerability assessment completed
- [ ] Security headers implemented
- [ ] Compliance requirements met