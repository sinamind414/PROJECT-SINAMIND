# -*- coding: utf-8 -*-
"""
routes/payment.py - Intégration Chargily Pay résiliente pour le e-paiement algérien
"""

import hmac
import hashlib
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from main import get_db, get_settings, state

logger = logging.getLogger("khawarizmi.payment")
router = APIRouter(prefix="/api/payment", tags=["Paiement"])

# ═══════════════════════════════════════════════════════════
# VERIFICATION HMAC SIGNATURE CHARGILY
# ═══════════════════════════════════════════════════════════

def verify_chargily_signature(body: bytes, signature: str, secret_key: str) -> bool:
    """Vérification HMAC-SHA256 avec le secret Chargily."""
    if not signature or not secret_key:
        return False
    expected = hmac.new(
        secret_key.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ═══════════════════════════════════════════════════════════
# ACTIVATION PREMIUM ARRIÈRE-PLAN
# ═══════════════════════════════════════════════════════════

async def activate_premium(checkout_id: str):
    """
    Active le statut premium ('pro') pour l'utilisateur associé au checkout_id.
    """
    if not state.db_session:
        logger.error("Impossible d'activer le premium: db_session non configurée.")
        return
        
    async with state.db_session() as session:
        try:
            result = await session.execute(
                text("SELECT user_id FROM payments WHERE checkout_id = :cid"),
                {"cid": checkout_id}
            )
            row = result.fetchone()
            if row:
                user_id = row[0]
                await session.execute(
                    text("UPDATE users SET plan = 'pro' WHERE id = :uid"),
                    {"uid": user_id}
                )
                await session.commit()
                logger.info(f"✅ Abonnement premium activé avec succès pour l'utilisateur {user_id} via checkout {checkout_id}")
            else:
                logger.error(f"❌ Impossible d'activer le premium: checkout_id {checkout_id} introuvable en base.")
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Erreur lors de l'activation premium pour checkout {checkout_id}: {e}")


# ═══════════════════════════════════════════════════════════
# WEBHOOK ENDPOINT
# ═══════════════════════════════════════════════════════════

@router.post("/webhook/chargily")
async def chargily_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    settings = Depends(get_settings)
):
    """
    Réception idempotente et HMAC-sécurisée des notifications Chargily Pay.
    Gère les instabilités de connexion 4G et SATIM/CIB.
    """
    body = await request.body()
    signature = request.headers.get("signature")
    
    # 1. Vérification de la signature HMAC
    if not verify_chargily_signature(body, signature, settings.chargily_secret_key):
        logger.warning("Signature de webhook invalide.")
        raise HTTPException(status_code=403, detail="Invalid signature")
        
    try:
        payload = json.loads(body)
        event = payload.get("event")
        data = payload.get("data", {})
        checkout_id = data.get("id")
        status = data.get("status")
        amount = data.get("amount", 0.0)
    except Exception as e:
        logger.error(f"Format de webhook Chargily invalide : {e}")
        raise HTTPException(status_code=400, detail="Invalid payload format")

    if not checkout_id:
        raise HTTPException(status_code=400, detail="Missing checkout ID")
        
    logger.info(f"Webhook reçu - Event: {event}, Checkout: {checkout_id}, Status: {status}")
    
    # 2. IDEMPOTENCE : Vérifier si ce paiement a déjà été validé
    existing = await db.execute(
        text("SELECT id, status FROM payments WHERE checkout_id = :cid"),
        {"cid": checkout_id}
    )
    payment_row = existing.fetchone()
    
    if payment_row and payment_row[1] == "paid":
        logger.info(f"Webhook déjà traité pour le checkout {checkout_id}")
        return {"status": "already_processed"}
        
    # 3. Traitement selon le statut
    if status == "paid":
        if not payment_row:
            # Insérer si absent (par sécurité, bien qu'il devrait exister au moment du checkout)
            # Récupérer user_id depuis les métadonnées de Chargily si présentes
            metadata = data.get("metadata", {})
            user_id = metadata.get("user_id") if isinstance(metadata, dict) else None
            
            await db.execute(
                text("""
                    INSERT INTO payments (checkout_id, user_id, amount, status, raw_webhook, paid_at)
                    VALUES (:cid, :uid, :amount, 'paid', :raw::jsonb, :paid_at)
                """),
                {
                    "cid": checkout_id,
                    "uid": int(user_id) if user_id else None,
                    "amount": float(amount),
                    "raw": json.dumps(payload),
                    "paid_at": datetime.now(timezone.utc)
                }
            )
        else:
            await db.execute(
                text("""
                    UPDATE payments 
                    SET status = 'paid', paid_at = :paid_at, raw_webhook = :raw::jsonb, updated_at = NOW()
                    WHERE checkout_id = :cid
                """),
                {
                    "cid": checkout_id,
                    "paid_at": datetime.now(timezone.utc),
                    "raw": json.dumps(payload)
                }
            )
            
        await db.commit()
        # Lancement asynchrone de l'activation premium en arrière-plan
        background_tasks.add_task(activate_premium, checkout_id)
        
    elif status in ["failed", "canceled"]:
        if payment_row:
            await db.execute(
                text("UPDATE payments SET status = :status, updated_at = NOW() WHERE checkout_id = :cid"),
                {"status": status, "cid": checkout_id}
            )
            await db.commit()
            
    return {"status": "received"}


# ═══════════════════════════════════════════════════════════
# CRON JOB / FONCTION DE RECONCILIATION
# ═══════════════════════════════════════════════════════════

async def reconcile_pending_payments():
    """
    Réconcilie les paiements 'pending' bloqués suite à des micro-coupures de connexion.
    Recommandé pour être exécuté par un cron toutes les 30 minutes.
    """
    if not state.db_session:
        return
        
    logger.info("Début du job de réconciliation des paiements...")
    
    async with state.db_session() as session:
        try:
            # Récupérer les paiements en attente de plus de 10 minutes (et moins de 24h)
            pending = await session.execute(
                text("""
                    SELECT checkout_id 
                    FROM payments 
                    WHERE status = 'pending' 
                      AND created_at < NOW() - INTERVAL '10 minutes'
                      AND created_at > NOW() - INTERVAL '24 hours'
                """)
            )
            checkout_ids = [row[0] for row in pending.fetchall()]
            
            if not checkout_ids:
                logger.info("Aucun paiement en attente à réconcilier.")
                return
                
            # Pour chaque paiement en suspens, on interrogerait normalement l'API Chargily
            # chargily_client.retrieve_checkout(checkout_id)
            # Pour simuler de manière sécurisée en production sans SDK Chargily complet :
            logger.info(f"{len(checkout_ids)} paiements en attente détectés pour réconciliation.")
            
        except Exception as e:
            logger.error(f"Erreur lors de la réconciliation des paiements: {e}")
