# Khawarizmi Pro — Application principale
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base
from routes import annales_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crée les tables au démarrage (dev) + seed automatique optionnel."""
    # En dev : crée toutes les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)

    # Seed automatique ? (à activer via variable d'env en dev)
    # import os
    # if os.getenv("AUTO_SEED") == "1":
    #     ...

    yield


app = FastAPI(
    title="Khawarizmi Pro — API",
    description="Plateforme éducative : annales, vidéos, manhadjiya et plus.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Routers ────────────────────────────────────────────────────────────
app.include_router(annales_router)


@app.get("/")
def racine():
    return {
        "message": "Bienvenue sur l'API Khawarizmi Pro",
        "docs": "/docs",
        "version": "1.0.0",
    }