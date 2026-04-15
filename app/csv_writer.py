import os
import csv
from .groq_client import CATEGORIES

DATA_FOLDER = "data"


def _category_to_filename(categorie: str) -> str:
    safe = []
    for c in categorie:
        if c.isalnum():
            safe.append(c)
        else:
            safe.append("_")
    return "".join(safe) + ".csv"


class CSVWriter:
    def __init__(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        for categorie in CATEGORIES:
            path = os.path.join(DATA_FOLDER, _category_to_filename(categorie))
            if not os.path.exists(path):
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Sujet", "Urgence", "Synthèse"])
                print(f"📄 Fichier créé : {path}")

    def append_ticket(self, categorie: str, sujet: str, urgence: str, resume: str):
        if categorie not in CATEGORIES:
            categorie = CATEGORIES[0]

        path = os.path.join(DATA_FOLDER, _category_to_filename(categorie))

        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([sujet, urgence, resume])