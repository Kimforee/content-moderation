from prometheus_client import Counter, Histogram

# Metrics
REQUEST_COUNT = Counter("request_count", "Total number of API requests", ["endpoint", "method"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency in seconds", ["endpoint"])

def record_request(endpoint: str, method: str, latency: float):
    """ Records API requests and latency """
    REQUEST_COUNT.labels(endpoint=endpoint, method=method).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
