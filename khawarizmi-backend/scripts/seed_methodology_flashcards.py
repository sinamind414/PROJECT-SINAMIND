"""Script d'insertion des flashcards méthodologiques dans FSRS"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from methodology.methodology_flashcards import get_all_methodology_flashcards


def seed():
    cards = get_all_methodology_flashcards()
    print(f"Nombre total de cartes méthodologiques : {len(cards)}")

    by_cat = {}
    for card in cards:
        cat = card.get("category", "unknown")
        by_cat.setdefault(cat, []).append(card)

    for cat, items in sorted(by_cat.items()):
        print(f"  - {cat}: {len(items)} cartes")

    print("\nLes cartes sont prêtes à être insérées dans le système FSRS.")
    print("Commande recommandée pour insertion en base :")
    print("  INSERT INTO flashcards (front, back, category, difficulty) VALUES ...")

    return cards


if __name__ == "__main__":
    seed()
