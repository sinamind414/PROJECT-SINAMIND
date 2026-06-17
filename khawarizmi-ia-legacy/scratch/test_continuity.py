import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from structuration import is_exercise_incomplete, merge_cross_page_exercises

# Test is_exercise_incomplete
assert is_exercise_incomplete(None) == False
assert is_exercise_incomplete({'exercises': []}) == False

# Test with incomplete signals
incomplete = is_exercise_incomplete({'exercises': [{'texte': 'يقسم هذا التمرين', 'is_complete': False}]})
assert incomplete == True, f'Expected True, got {incomplete}'

incomplete2 = is_exercise_incomplete({'exercises': [{'texte': 'نص قصير', 'is_complete': True}]})
assert incomplete2 == True, 'Short text should be detected as incomplete'

complete = is_exercise_incomplete({'exercises': [{'texte': 'نص كامل ينتهي بنقطة.', 'is_complete': True}]})
assert complete == False, f'Expected False, got {complete}'

# Test merge_cross_page_exercises
pages_data = [
    {
        'page_number': 11,
        'exercises': [
            {'id': 'ex_11_1', 'texte': 'Début exercice', 'is_complete': False, 'questions': ['q1']}
        ]
    },
    {
        'page_number': 12,
        'exercises': [
            {'id': 'ex_12_1', 'texte': 'Suite exercice', 'is_complete': True, 'questions': ['q2']}
        ]
    }
]

merged = merge_cross_page_exercises(pages_data)
print(f'Fusionnés : {len(merged)} exercices')
for ex in merged:
    print(f'  Texte: "{ex["texte"]}" | Pages: {ex["pages_source"]} | Questions: {ex["questions"]}')

assert len(merged) == 1
assert merged[0]['pages_source'] == [11, 12]
assert merged[0]['texte'] == 'Début exercice\nSuite exercice'
print('Tous les tests passent!')
