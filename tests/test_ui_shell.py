def test_ui_shell_is_served(client):
    response = client.get("/app/")

    assert response.status_code == 200
    assert "Sign in to your wallet" in response.text
    assert "login-form" in response.text
    assert "register-form" in response.text
    assert "wallet-form" in response.text
    assert "./styles.css" in response.text
    assert "./app.js" in response.text


def test_ui_static_assets_are_served(client):
    stylesheet = client.get("/app/styles.css")
    javascript = client.get("/app/app.js")

    assert stylesheet.status_code == 200
    assert javascript.status_code == 200

    assert "text/css" in stylesheet.headers["content-type"]
    assert "javascript" in javascript.headers["content-type"]