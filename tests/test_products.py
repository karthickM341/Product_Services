def product_payload(**overrides):
    data = {"name": "Desk Lamp", "description": "LED lamp", "price": "25.50",
            "quantity": 12, "category": "Lighting", "status": "ACTIVE"}
    data.update(overrides)
    return data

def test_create_and_get_product(client):
    response = client.post("/api/v1/products", json=product_payload())
    assert response.status_code == 201
    assert response.headers["location"].endswith(f"/{response.json()['id']}")
    product_id = response.json()["id"]
    got = client.get(f"/api/v1/products/{product_id}")
    assert got.status_code == 200
    assert got.json()["name"] == "Desk Lamp"

def test_validation_failure(client):
    response = client.post("/api/v1/products", json=product_payload(price="0"))
    assert response.status_code == 400
    assert response.json()["error"] == "Bad Request"
    assert "details" in response.json()

def test_duplicate_name_case_insensitive(client):
    client.post("/api/v1/products", json=product_payload())
    response = client.post("/api/v1/products", json=product_payload(name=" desk lamp "))
    assert response.status_code == 409

def test_not_found(client):
    response = client.get("/api/v1/products/999")
    assert response.status_code == 404

def test_list_filter_sort_pagination(client):
    client.post("/api/v1/products", json=product_payload())
    client.post("/api/v1/products", json=product_payload(name="Chair", category="Furniture", price="80.00"))
    response = client.get("/api/v1/products?page=0&size=1&sort=price,asc")
    assert response.status_code == 200
    body = response.json()
    assert body["size"] == 1
    assert body["totalItems"] == 2
    assert body["totalPages"] == 2

def test_put_patch_delete(client):
    created = client.post("/api/v1/products", json=product_payload()).json()
    pid = created["id"]
    patched = client.patch(f"/api/v1/products/{pid}", json={"quantity": 20})
    assert patched.status_code == 200 and patched.json()["quantity"] == 20
    replacement = product_payload(name="New Lamp")
    assert client.put(f"/api/v1/products/{pid}", json=replacement).status_code == 200
    assert client.delete(f"/api/v1/products/{pid}").status_code == 204
    assert client.get(f"/api/v1/products/{pid}").status_code == 404

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"
