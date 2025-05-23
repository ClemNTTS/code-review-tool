import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_lint_python():
    response = client.post(
        "/functions/run_linter",
        json={"language": "python", "code": "def add(a, b):\n    return a+b\n"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_lint_javascript():
    response = client.post(
        "/functions/run_linter",
        json={"language": "javascript", "code": "var unused; function add(a,b){return a+b;}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), (dict, list))

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"lint_requests_total" in response.content

def test_lint_python_invalid_json():
    # Simule une sortie flake8 non JSON pour forcer une erreur
    from unittest.mock import patch

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "not a json"
        mock_run.return_value.stderr = "flake8 error"
        response = client.post(
            "/functions/run_linter",
            json={"language": "python", "code": "def add(a, b):\n    return a+b\n"}
        )
        assert response.status_code == 200
        assert "error" in response.json()
