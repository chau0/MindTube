# TASK-030: Performance Testing

## Task Information
- **ID**: TASK-030
- **Phase**: 6 - Testing & Quality Assurance
- **Estimate**: 75 minutes
- **Dependencies**: TASK-029
- **Status**: 🔴 Backlog

## Description
Create comprehensive performance and load tests to ensure the application meets performance requirements under various conditions. Establish performance baselines and regression testing capabilities.

## Acceptance Criteria
- [ ] Test processing time targets for different video lengths
- [ ] Test memory usage patterns and limits
- [ ] Test concurrent request handling capacity
- [ ] Test cache performance and hit rates
- [ ] Add performance regression tests
- [ ] Create load testing scenarios
- [ ] Document performance baselines and SLAs

## Implementation Details

### Performance Requirements

#### Processing Time Targets
```
Video Length    | Target Processing Time | Max Memory Usage
5 minutes      | < 30 seconds          | < 512MB
15 minutes     | < 60 seconds          | < 1GB
30 minutes     | < 120 seconds         | < 2GB
60 minutes     | < 300 seconds         | < 4GB
```

#### API Response Targets
```
Endpoint       | Target Response Time | 95th Percentile
/health        | < 100ms             | < 200ms
/analyze       | < 60s               | < 120s
/transcript    | < 30s               | < 60s
/summarize     | < 45s               | < 90s
```

### Test Structure

#### Performance Test Suite
```
tests/performance/
├── test_processing_performance.py
├── test_api_performance.py
├── test_memory_usage.py
├── test_concurrent_load.py
├── test_cache_performance.py
├── benchmarks/
│   ├── baseline_results.json
│   └── regression_thresholds.json
└── load_scenarios/
    ├── light_load.py
    ├── normal_load.py
    └── stress_load.py
```

#### Core Performance Tests
```python
# tests/performance/test_processing_performance.py
import pytest
import time
import psutil
import os
from mindtube.core.engine import MindTubeEngine

class TestProcessingPerformance:
    
    @pytest.mark.performance
    @pytest.mark.parametrize("video_length,max_time", [
        ("5min", 30),
        ("15min", 60),
        ("30min", 120),
    ])
    def test_processing_time_by_video_length(self, video_length, max_time):
        """Test processing time meets targets for different video lengths"""
        engine = MindTubeEngine()
        transcript = load_test_transcript(video_length)
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        result = engine.process_transcript(transcript)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert processing_time < max_time, f"Processing took {processing_time}s, expected < {max_time}s"
        assert result is not None
        
        # Log performance metrics
        log_performance_metric("processing_time", video_length, processing_time)
        log_performance_metric("memory_usage", video_length, memory_used)
    
    @pytest.mark.performance
    def test_memory_usage_large_transcript(self):
        """Test memory usage with large transcripts"""
        engine = MindTubeEngine()
        large_transcript = create_large_transcript(60)  # 60 minute transcript
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        result = engine.process_transcript(large_transcript)
        
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - initial_memory
        
        assert memory_increase < 4096, f"Memory usage {memory_increase}MB exceeds 4GB limit"
        assert result is not None
```

#### API Performance Tests
```python
# tests/performance/test_api_performance.py
import asyncio
import time
from fastapi.testclient import TestClient
from mindtube.api.app import app

class TestAPIPerformance:
    
    @pytest.mark.performance
    def test_health_endpoint_response_time(self):
        """Test health endpoint responds quickly"""
        client = TestClient(app)
        
        response_times = []
        for _ in range(100):
            start = time.time()
            response = client.get("/health")
            end = time.time()
            
            assert response.status_code == 200
            response_times.append(end - start)
        
        avg_time = sum(response_times) / len(response_times)
        p95_time = sorted(response_times)[94]  # 95th percentile
        
        assert avg_time < 0.1, f"Average response time {avg_time}s > 100ms"
        assert p95_time < 0.2, f"95th percentile {p95_time}s > 200ms"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_analyze_requests(self):
        """Test handling multiple concurrent analyze requests"""
        client = TestClient(app)
        
        async def make_request():
            response = client.post("/analyze", json={
                "url": "https://youtu.be/test_video",
                "options": {"include_summary": True}
            })
            return response.status_code, response.elapsed.total_seconds()
        
        # Run 10 concurrent requests
        start_time = time.time()
        results = asyncio.run(run_concurrent_requests(make_request, 10))
        total_time = time.time() - start_time
        
        success_count = sum(1 for status, _ in results if status == 200)
        avg_response_time = sum(time for _, time in results) / len(results)
        
        assert success_count >= 8, f"Only {success_count}/10 requests succeeded"
        assert total_time < 180, f"Total time {total_time}s too long for concurrent requests"
        assert avg_response_time < 120, f"Average response time {avg_response_time}s too slow"
```

#### Cache Performance Tests
```python
# tests/performance/test_cache_performance.py
class TestCachePerformance:
    
    @pytest.mark.performance
    def test_cache_hit_performance(self):
        """Test cache hit performance"""
        cache = CacheAdapter()
        test_key = "test_transcript_key"
        test_data = create_test_transcript_data()
        
        # Warm up cache
        cache.set(test_key, test_data)
        
        # Test cache hit performance
        hit_times = []
        for _ in range(1000):
            start = time.time()
            result = cache.get(test_key)
            end = time.time()
            
            assert result is not None
            hit_times.append(end - start)
        
        avg_hit_time = sum(hit_times) / len(hit_times)
        assert avg_hit_time < 0.001, f"Cache hit time {avg_hit_time}s too slow"
    
    @pytest.mark.performance
    def test_cache_miss_performance(self):
        """Test cache miss handling performance"""
        cache = CacheAdapter()
        
        miss_times = []
        for i in range(100):
            start = time.time()
            result = cache.get(f"nonexistent_key_{i}")
            end = time.time()
            
            assert result is None
            miss_times.append(end - start)
        
        avg_miss_time = sum(miss_times) / len(miss_times)
        assert avg_miss_time < 0.01, f"Cache miss time {avg_miss_time}s too slow"
```

### Load Testing

#### Load Test Scenarios
```python
# tests/performance/load_scenarios/normal_load.py
import locust
from locust import HttpUser, task, between

class NormalLoadUser(HttpUser):
    wait_time = between(5, 15)  # 5-15 seconds between requests
    
    @task(3)
    def analyze_video(self):
        """Simulate normal video analysis requests"""
        self.client.post("/analyze", json={
            "url": "https://youtu.be/sample_video",
            "options": {"include_summary": True, "include_mindmap": True}
        })
    
    @task(1)
    def get_health(self):
        """Health check requests"""
        self.client.get("/health")
    
    @task(2)
    def get_transcript(self):
        """Transcript-only requests"""
        self.client.post("/transcript", json={
            "url": "https://youtu.be/sample_video"
        })

# Run with: locust -f normal_load.py --host=http://localhost:8000
```

#### Stress Testing
```python
# tests/performance/load_scenarios/stress_load.py
class StressLoadUser(HttpUser):
    wait_time = between(1, 3)  # Aggressive timing
    
    @task
    def stress_analyze(self):
        """High-frequency analysis requests"""
        self.client.post("/analyze", json={
            "url": f"https://youtu.be/video_{random.randint(1, 100)}",
            "options": {"include_summary": True}
        })

# Target: 100 concurrent users, 1000 requests/minute
```

### Performance Monitoring

#### Metrics Collection
```python
# tests/performance/metrics.py
import json
import time
from pathlib import Path

class PerformanceMetrics:
    def __init__(self):
        self.metrics = {}
        self.baseline_file = Path("tests/performance/benchmarks/baseline_results.json")
    
    def record_metric(self, test_name: str, metric_name: str, value: float):
        """Record a performance metric"""
        if test_name not in self.metrics:
            self.metrics[test_name] = {}
        self.metrics[test_name][metric_name] = value
    
    def compare_to_baseline(self, tolerance: float = 0.1):
        """Compare current metrics to baseline"""
        if not self.baseline_file.exists():
            self.save_baseline()
            return True
        
        with open(self.baseline_file) as f:
            baseline = json.load(f)
        
        regressions = []
        for test_name, metrics in self.metrics.items():
            if test_name in baseline:
                for metric_name, value in metrics.items():
                    baseline_value = baseline[test_name].get(metric_name)
                    if baseline_value and value > baseline_value * (1 + tolerance):
                        regressions.append(f"{test_name}.{metric_name}: {value} > {baseline_value}")
        
        return len(regressions) == 0, regressions
    
    def save_baseline(self):
        """Save current metrics as baseline"""
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
```

### CI Integration

#### Performance Test Pipeline
```yaml
# .github/workflows/performance-tests.yml
name: Performance Tests

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  performance-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        make install-deps
        make install-dev-deps
        pip install locust
    
    - name: Run performance tests
      run: |
        pytest tests/performance -m performance --tb=short
    
    - name: Run load tests
      run: |
        locust -f tests/performance/load_scenarios/normal_load.py \
               --host=http://localhost:8000 \
               --users=50 \
               --spawn-rate=5 \
               --run-time=300s \
               --headless
    
    - name: Upload performance results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: tests/performance/benchmarks/
```

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Performance baselines established
- [ ] Load testing scenarios implemented
- [ ] Performance regression detection working
- [ ] CI pipeline includes performance tests
- [ ] Performance documentation updated
- [ ] SLA targets documented and tested