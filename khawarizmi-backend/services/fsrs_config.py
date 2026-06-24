"""
services/fsrs_config.py - Configuration FSRS dynamique selon le calendrier scolaire algérien.
"""

import logging
from datetime import date

from fsrs import Scheduler

logger = logging.getLogger("khawarizmi.fsrs_config")


def get_fsrs_scheduler(user_fsrs_config: dict | None = None) -> Scheduler:
    """
    Retourne un scheduler FSRS (Scheduler) calibré.
    Si user_fsrs_config contient desired_retention ou d'autres paramètres, on les applique,
    sinon on applique le taux de rétention dynamique selon la période de l'année.
    Le BAC algérien SVT est généralement début juin.
    """
    desired_retention = 0.85

    if user_fsrs_config and "desired_retention" in user_fsrs_config:
        desired_retention = user_fsrs_config["desired_retention"]
    else:
        today = date.today()
        # Approximation de la date du BAC: 5 juin de l'année courante (ou suivante si déjà passé juin)
        year = today.year
        if today.month > 6 or (today.month == 6 and today.day > 10):
            year += 1
        bac_date = date(year, 6, 5)
        days_to_bac = (bac_date - today).days

        if days_to_bac > 90:  # Phase 1 : Apprentissage progressif (Septembre - Mars)
            desired_retention = 0.82
            phase = "apprentissage"
        elif days_to_bac > 15:  # Phase 2 : Révisions intensives (Avril - Mai)
            desired_retention = 0.87
            phase = "revisions"
        else:  # Phase 3 : Sprint final (J-15 avant le BAC)
            desired_retention = 0.90
            phase = "sprint_final"

        logger.info(
            f"FSRS calibration dynamique - Phase: {phase}, Retention cible: {desired_retention:.2f}, Jours restants BAC: {days_to_bac}"
        )

    kwargs = {"desired_retention": desired_retention}

    if user_fsrs_config:
        # FSRS standard Scheduler v4+ utilise w[] de 17 ou 19 float
        if "w" in user_fsrs_config:
            kwargs["w"] = user_fsrs_config["w"]
        # d'autres attributs de configuration
        for key in ["request_retention", "maximum_interval", "enable_fuzzing"]:
            if key in user_fsrs_config:
                kwargs[key] = user_fsrs_config[key]

    try:
        scheduler = Scheduler(**kwargs)
    except TypeError as e:
        logger.warning(
            f"Paramètres FSRS non supportés par le constructeur Scheduler ({e}), fallback avec desired_retention={desired_retention}"
        )
        scheduler = Scheduler(desired_retention=desired_retention)

    return scheduler
