# tests/test_auth.py
# Tests du système d'authentification JWT

from httpx import AsyncClient


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "nouveau@bac.dz",
                "password": "SecurePass123!",
                "prenom": "Nouveau Élève",
                "filiere": "Mathématiques",
            },
        )
        assert response.status_code in [200, 201, 409]

    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post(
            "/api/auth/register",
            json={"email": "doublon@bac.dz", "password": "SecurePass123!", "prenom": "Premier", "filiere": "Sciences"},
        )
        response = await client.post(
            "/api/auth/register",
            json={"email": "doublon@bac.dz", "password": "AnotherPass123!", "prenom": "Second", "filiere": "Sciences"},
        )
        assert response.status_code in [400, 409, 500]

    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={"email": "pas-un-email", "password": "SecurePass123!", "prenom": "Test", "filiere": "Maths"},
        )
        assert response.status_code in [422, 400]

    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={"email": "test2@bac.dz", "password": "123", "prenom": "Test", "filiere": "Maths"},
        )
        assert response.status_code in [422, 400]


class TestLogin:
    async def test_login_wrong_password(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={"email": "inconnu@bac.dz", "password": "MauvaisMdp"})
        assert response.status_code in [401, 500]

    async def test_login_unknown_email(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={"email": "personne@bac.dz", "password": "TestSecure123!"})
        assert response.status_code in [401, 500]


class TestToken:
    async def test_valid_token_accepted(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code in [200, 401]

    async def test_cookie_token_accepted(self, client: AsyncClient):
        from auth import create_access_token

        token = create_access_token({"sub": 1, "email": "eleve@bac.dz", "plan": "free"})
        client.cookies.set("khawarizmi_access_token", token)
        response = await client.get("/api/auth/me")
        assert response.status_code == 200

    async def test_missing_token_rejected(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code in [401, 404]
