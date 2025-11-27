from app import create_app

def test_homepage_status():
    app = create_app()
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
