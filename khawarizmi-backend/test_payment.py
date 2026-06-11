# -*- coding: utf-8 -*-
"""
test_payment.py - Tests unitaires pour l'intégration Chargily Pay
"""

import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

# Force environment variable for config
import os
os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-testing"

from main import app, get_db, get_settings
from routes.payment import verify_chargily_signature

client = TestClient(app)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION ET FIXTURES
# ═══════════════════════════════════════════════════════════

SECRET_KEY = "test_secret_key_123"

class MockSettings:
    chargily_secret_key = SECRET_KEY

def override_get_settings():
    return MockSettings()

# Overrides
app.dependency_overrides[get_settings] = override_get_settings

global_mock_db = MagicMock()
global_mock_db.execute = AsyncMock()

async def global_override_get_db():
    yield global_mock_db

app.dependency_overrides[get_db] = global_override_get_db


def test_verify_signature():
    body = b'{"event":"checkout.paid","data":{"id":"chk_123"}}'
    signature = hmac.new(SECRET_KEY.encode("utf-8"), body, hashlib.sha256).hexdigest()
    
    assert verify_chargily_signature(body, signature, SECRET_KEY) is True
    assert verify_chargily_signature(body, "wrong_sig", SECRET_KEY) is False


def test_webhook_invalid_signature():
    response = client.post(
        "/api/payment/webhook/chargily",
        content='{"event":"checkout.paid"}',
        headers={"signature": "bad_sig"}
    )
    assert response.status_code == 403
    assert response.json() == {
        "erreur": "Invalid signature",
        "status": 403,
        "path": "/api/payment/webhook/chargily"
    }


@pytest.mark.asyncio
async def test_webhook_paid_success():
    body_dict = {
        "event": "checkout.paid",
        "data": {
            "id": "chk_999",
            "status": "paid",
            "amount": 990.00,
            "metadata": {
                "user_id": "42"
            }
        }
    }
    body_bytes = json.dumps(body_dict).encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
    
    # Mock Database session execution
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None 
    
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    
    # Override get_db to return our mocked DB session
    async def override_get_db():
        yield mock_db
        
    app.dependency_overrides[get_db] = override_get_db
    
    # Mock background tasks / AppState sessionmaker
    with patch("routes.payment.state") as mock_state:
        mock_result_session = MagicMock()
        mock_result_session.fetchone.return_value = (42,) # user_id = 42
        
        mock_session = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result_session)
        mock_session.commit = AsyncMock()
        
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_state.db_session = mock_session_maker
        
        response = client.post(
            "/api/payment/webhook/chargily",
            content=json.dumps(body_dict),
            headers={"signature": signature}
        )
        
        assert response.status_code == 200
        assert response.json() == {"status": "received"}
        
        # Verify database inserts
        assert mock_db.execute.called
        assert mock_db.commit.called
        
        # Verify activation premium background task
        from routes.payment import activate_premium
        await activate_premium("chk_999")
        assert mock_session.execute.called
        assert mock_session.commit.called


@pytest.mark.asyncio
async def test_webhook_idempotency():
    body_dict = {
        "event": "checkout.paid",
        "data": {
            "id": "chk_already_paid",
            "status": "paid",
            "amount": 990.00
        }
    }
    body_bytes = json.dumps(body_dict).encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
    
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (1, "paid")
    
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    async def override_get_db():
        yield mock_db
        
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.post(
        "/api/payment/webhook/chargily",
        content=json.dumps(body_dict),
        headers={"signature": signature}
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "already_processed"}
    
    # Commit shouldn't be called since it was already processed
    assert not mock_db.commit.called
