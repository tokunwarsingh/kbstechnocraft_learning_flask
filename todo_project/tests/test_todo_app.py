def test_browser_and_api_share_persistent_todo(client):
    response = client.post("/todos", data={"title": "Learn Flask"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Learn Flask" in response.data

    response = client.get("/api/todos")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["title"] == "Learn Flask"


def test_api_can_update_and_delete_todo(client):
    created = client.post("/api/todos", json={"title": "Build an API"})
    todo_id = created.get_json()["id"]

    updated = client.patch(
        f"/api/todos/{todo_id}",
        json={"completed": True, "title": "Build a tested API"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["completed"] is True
    assert updated.get_json()["title"] == "Build a tested API"

    deleted = client.delete(f"/api/todos/{todo_id}")
    assert deleted.status_code == 204
    assert client.get("/api/todos").get_json()["items"] == []


def test_api_rejects_invalid_title(client):
    response = client.post("/api/todos", json={"title": "   "})

    assert response.status_code == 400
    assert response.get_json()["error"] == "title must be 1 to 200 characters"


def test_missing_api_todo_returns_404(client):
    response = client.patch("/api/todos/999", json={"completed": True})

    assert response.status_code == 404
    assert response.get_json()["error"] == "Todo not found"
