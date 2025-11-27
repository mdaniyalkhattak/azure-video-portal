import os
import pytest

# Skip this entire test module if Azure credentials are missing (CI environment)
if not os.getenv("AZURE_BLOB_CONNECTION_STRING"):
    pytest.skip("Skipping smoke test because Azure credentials are missing in CI", allow_module_level=True)

from app import create_app

def test_homepage_loads():
    """Simple test to ensure the homepage loads in a testing environment."""
    app = create_app()
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
