file_path = 'backend/tests/test_auth.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

tests_to_add = """
def test_change_password_success(db):
    res = client.post("/api/auth/token", data={"username": "reviewer", "password": "demo123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    change_res = client.post("/api/auth/change-password", json={"current_password": "demo123", "new_password": "newpassword123"}, headers=headers)
    assert change_res.status_code == 200
    
    # Old password should fail
    fail_res = client.post("/api/auth/token", data={"username": "reviewer", "password": "demo123"})
    assert fail_res.status_code == 401
    
    # New password should succeed
    success_res = client.post("/api/auth/token", data={"username": "reviewer", "password": "newpassword123"})
    assert success_res.status_code == 200

def test_change_password_wrong_current(db):
    res = client.post("/api/auth/token", data={"username": "operator", "password": "demo123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    change_res = client.post("/api/auth/change-password", json={"current_password": "wrongpassword", "new_password": "newpassword123"}, headers=headers)
    assert change_res.status_code == 400
    assert change_res.json()["detail"] == "Incorrect current password"
"""

content += tests_to_add

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
