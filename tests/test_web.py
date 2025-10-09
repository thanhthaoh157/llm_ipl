from __future__ import annotations

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from uoa_toolkit.web import create_fastapi_app, create_flask_app


SAMPLE_RECIPE = PROJECT_ROOT / "recipes" / "sample.yaml"


def test_fastapi_run_endpoint(tmp_path):
    pytest.importorskip("fastapi")
    pytest.importorskip("starlette")
    app = create_fastapi_app()
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.post(
        "/api/run",
        json={
            "recipe_path": str(SAMPLE_RECIPE),
            "output_dir": str(tmp_path / "fastapi"),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["row_count"] > 0
    for path in payload["exports"].values():
        assert Path(path).exists()


def test_flask_run_endpoint(tmp_path):
    pytest.importorskip("flask")
    app = create_flask_app()
    client = app.test_client()
    response = client.post(
        "/api/run",
        json={
            "recipe_path": str(SAMPLE_RECIPE),
            "output_dir": str(tmp_path / "flask"),
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["column_count"] > 0
    for path in payload["exports"].values():
        assert Path(path).exists()
