"""Unit tests for Rate Limiting, Brute-Force Lockout, and Security Headers."""

import pytest
from fastapi import HTTPException, Response
from RevOpsAI.src.api.rate_limiter import SlidingWindowRateLimiter, rate_limiter, get_client_ip
from RevOpsAI.src.api.routes import (
    login_session,
    public_website_diagnostic,
    LoginRequest,
    PublicDiagnosticRequest,
)
from RevOpsAI.src.api.main import root_landing


def test_rate_limiter_sliding_window():
    """Verify rate limiter allows up to limit and blocks with Retry-After afterwards."""
    limiter = SlidingWindowRateLimiter()
    key = "test_user_ip"

    # Should allow 3 requests
    for _ in range(3):
        is_limited, _ = limiter.is_rate_limited(key, max_requests=3, window_seconds=10.0)
        assert not is_limited

    # 4th request must be limited
    is_limited, retry_sec = limiter.is_rate_limited(key, max_requests=3, window_seconds=10.0)
    assert is_limited
    assert retry_sec > 0


def test_rate_limiter_brute_force_lockout():
    """Verify 5 failed attempts trigger brute force lockout."""
    limiter = SlidingWindowRateLimiter()
    key = "fail:192.168.1.1:admin"

    for _ in range(4):
        limiter.record_failure(key)
        is_locked, _ = limiter.is_brute_force_locked(key, max_failures=5, lock_window_seconds=60.0)
        assert not is_locked

    # 5th failure triggers lockout
    limiter.record_failure(key)
    is_locked, retry_sec = limiter.is_brute_force_locked(key, max_failures=5, lock_window_seconds=60.0)
    assert is_locked
    assert retry_sec > 0

    # Reset failure on success clears the lockout
    limiter.reset_failures(key)
    is_locked, _ = limiter.is_brute_force_locked(key, max_failures=5, lock_window_seconds=60.0)
    assert not is_locked


def test_login_brute_force_lockout_endpoint():
    """Verify login_session endpoint returns 429 Too Many Requests after repeated bad attempts."""
    rate_limiter.clear()
    resp = Response()
    bad_req = LoginRequest(username="attacker@hzsaas.com", password="wrongpassword", mode="REVOPS")

    # First 4 attempts return 401 Unauthorized
    for _ in range(4):
        with pytest.raises(HTTPException) as exc_info:
            login_session(bad_req, resp)
        assert exc_info.value.status_code == 401

    # 5th bad attempt triggers 401 and records 5th failure
    with pytest.raises(HTTPException) as exc_info:
        login_session(bad_req, resp)
    assert exc_info.value.status_code == 401

    # 6th attempt is blocked with 429 Too Many Requests
    with pytest.raises(HTTPException) as exc_info:
        login_session(bad_req, resp)
    assert exc_info.value.status_code == 429
    assert "Acceso temporalmente pausado" in exc_info.value.detail
    assert "Retry-After" in exc_info.value.headers

    rate_limiter.clear()


def test_public_diagnostic_rate_limit():
    """Verify /public/diagnostic rate limits after 10 requests per minute."""
    rate_limiter.clear()
    req = PublicDiagnosticRequest(
        name="Clínica Test",
        url="https://example.com",
        sector="clinicas",
    )

    # First 10 requests should process or succeed
    for _ in range(10):
        res = public_website_diagnostic(req)
        assert "score" in res

    # 11th request must raise 429 Too Many Requests
    with pytest.raises(HTTPException) as exc_info:
        public_website_diagnostic(req)
    assert exc_info.value.status_code == 429
    assert "Límite de solicitudes de diagnóstico alcanzado" in exc_info.value.detail

    rate_limiter.clear()


def test_landing_page_monteria_reference():
    """Verify landing page correctly references Montería, Colombia."""
    res = root_landing()
    assert res.status_code == 200
    html = res.body.decode("utf-8")
    assert "Montería, Colombia" in html
    assert "Medellín, Colombia" not in html
