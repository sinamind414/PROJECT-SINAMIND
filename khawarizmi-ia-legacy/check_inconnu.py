import json

with open('corpus/sciences_bac_exercices.json', encoding='utf-8') as f:
    exs = json.load(f)

print('--- EXERCICES INCONNUS ---')
for ex in exs:
    if ex['chapitre_id'] == 'ch_inconnu':
        print(f"ID: {ex['id']}")
        print(f"Enonce: {ex['enonce']}")
        print('-'*40)

with open('corpus/sciences_methodologie.json', encoding='utf-8') as f:
    meths = json.load(f)

for meth in meths:
    if meth['chapitre_id'] == 'ch_inconnu':
        print(f"[Methode] ID: {meth['id']}")
        print(f"Enonce: {meth['enonce']}")
        print('-'*40)
