"""
Unit and Integration Tests for Authentication, Password Security, and Evaluation Pipeline
Validates PBKDF2 hashing, salt generation, token verification, RBAC route protection,
no plaintext password storage, and mocked evaluation file generation.
"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from backend.app.services.admin_service import get_admin_service


@pytest.fixture
def client():
    return TestClient(app)


def test_password_hashing_pbkdf2():
    """Verify PBKDF2 200,000 iteration salted hashing format and uniqueness."""
    pwd = "SecretPassword123!"
    h1 = hash_password(pwd)
    h2 = hash_password(pwd)

    # Format must be pbkdf2_sha256$200000$<salt>$<hash>
    assert h1.startswith("pbkdf2_sha256$200000$")
    assert h2.startswith("pbkdf2_sha256$200000$")

    # Salts must be random, so hashes must differ
    assert h1 != h2

    # Verification must succeed for correct password
    assert verify_password(pwd, h1) is True
    assert verify_password(pwd, h2) is True

    # Verification must fail for wrong password
    assert verify_password("WrongPassword!", h1) is False

    # Plaintext equality matching must be strictly rejected
    assert verify_password(pwd, pwd) is False
    assert verify_password("admin123", "admin123") is False


def test_passwords_never_stored_in_plaintext_in_db():
    """Verify all users in the SQLite database have PBKDF2 hashed passwords."""
    admin_svc = get_admin_service()
    users = admin_svc.list_users(limit=100)
    assert users["total"] >= 2

    # Verify list_users NEVER returns password or password_hash fields to API callers
    for u in users["users"]:
        assert "password" not in u
        assert "password_hash" not in u

    # Check underlying DB storage
    raw_user = admin_svc.get_user_by_username("admin")
    assert raw_user is not None
    stored = raw_user.get("password", "")
    assert stored.startswith("pbkdf2_sha256$200000$"), f"Password stored in plaintext: {stored}"
    assert "admin123" not in stored


def test_auth_login_endpoint(client):
    """Test POST /api/v1/auth/login endpoint."""
    # 1. Incorrect credentials -> 401
    r_bad = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong_password"})
    assert r_bad.status_code == 401

    # 2. Correct credentials -> 200 and access_token
    r_ok = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert r_ok.status_code == 200
    data = r_ok.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["username"] == "admin"


def test_admin_route_protection_and_rbac(client):
    """Admin routes must return 401 without token, 403 for non-admin, 200 for admin."""
    admin_token = create_access_token({"sub": "admin", "user_id": "usr_001", "role": "admin"})
    user_token = create_access_token({"sub": "user", "user_id": "usr_002", "role": "user"})

    # 1. No token -> 401
    r_no_auth = client.get("/api/v1/admin/users")
    assert r_no_auth.status_code == 401

    r_no_auth_eval = client.get("/api/v1/admin/evaluation/latest")
    assert r_no_auth_eval.status_code == 401

    # 2. Non-admin user token -> 403 Forbidden
    r_user = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {user_token}"})
    assert r_user.status_code == 403

    # 3. Admin token -> 200 OK
    r_admin = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r_admin.status_code == 200
    assert "users" in r_admin.json()


def test_run_evaluation_writes_valid_results_file():
    """Verify run_evaluation execution with mocked LLM client writes a valid latest.json file."""
    from backend.app.evaluation.benchmark_dataset import BENCHMARK_TEST_CASES
    from backend.app.evaluation.evaluator import RAGEvaluator

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test_eval_results.json")

        evaluator = RAGEvaluator()
        # Evaluate a small slice of test cases
        test_slice = BENCHMARK_TEST_CASES[:2]

        with patch("backend.app.core.llm_client.OpenRouterLLMClient.call_chat_completion") as mock_llm:
            mock_llm.return_value = json.dumps({
                "faithfulness": 0.95,
                "answer_relevancy": 0.90,
                "contextual_precision": 0.85,
                "contextual_recall": 0.88,
                "recommendation_quality": 0.92
            })

            # Run evaluation on slice (max_cases=2)
            results = evaluator.run_benchmark_evaluation(output_dir=tmpdir, max_cases=2)

            latest_file = os.path.join(tmpdir, "latest.json")
            assert os.path.exists(latest_file)
            with open(latest_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert "retrieval_benchmarks" in saved_data
            assert "aggregate_deepeval_metrics" in saved_data
            assert saved_data["total_benchmark_cases"] == 2
