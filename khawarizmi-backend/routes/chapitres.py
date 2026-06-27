from fastapi import APIRouter, Depends, HTTPException

from deps import get_current_user, get_tutor
from services.khawarizmi_engine import KhawarizmiTutor

router = APIRouter(tags=["Contenu"])


@router.get("/api/chapitres/{matiere}")
async def get_chapitres(
    matiere: str,
    current_user: dict = Depends(get_current_user),
    tutor: KhawarizmiTutor = Depends(get_tutor),
):
    if hasattr(tutor, "programme_canonical") and tutor.programme_canonical:
        programme = tutor.programme_canonical
    else:
        programme = {
            "maths": tutor.programme_maths,
            "physique": tutor.programme_physique,
            "sciences": tutor.programme_sciences,
        }.get(matiere)

    if not programme:
        raise HTTPException(status_code=404, detail=f"Matière '{matiere}' introuvable")

    chapitres = programme.get("chapitres", [])

    return {
        "matiere": matiere,
        "nb_chapitres": len(chapitres),
        "chapitres": [
            {
                "id": ch.get("id"),
                "nom": ch.get("nom"),
                "nb_micro_concepts": len(ch.get("micro_concepts", [])),
            }
            for ch in chapitres
        ],
    }
