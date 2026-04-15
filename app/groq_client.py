import os
import json
from groq import Groq

CATEGORIES = [
    "Problème technique informatique",
    "Demande administrative",
    "Problème d'accès / authentification",
    "Demande de support utilisateur",
    "Bug ou dysfonctionnement d'un service",
]

URGENCES = [
    "Anodine",
    "Faible",
    "Modérée",
    "Élevée",
    "Critique",
]

SYSTEM_PROMPT = f"""Tu es un assistant expert en gestion de tickets de support informatique.
Pour chaque email reçu, tu dois analyser le sujet et le contenu puis retourner UNIQUEMENT un objet JSON valide (sans texte autour, sans balises markdown).

Règles strictes :
- "categorie" doit être EXACTEMENT l'une de ces valeurs : {json.dumps(CATEGORIES, ensure_ascii=False)}
- "urgence" doit être EXACTEMENT l'une de ces valeurs : {json.dumps(URGENCES, ensure_ascii=False)}
- "resume" : résumé clair en français, 1 à 3 phrases maximum

Format de réponse attendu :
{{"categorie": "...", "urgence": "...", "resume": "..."}}"""


class TicketClassifier:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY manquant dans le fichier .env")

        self.client     = Groq(api_key=api_key)
        self.model_name =  "llama-3.3-70b-versatile"

    def classify(self, subject: str, body: str) -> dict:
        user_content = f"Sujet : {subject}\n\nContenu :\n{body[:2000]}"

        completion = self.client.chat.completions.create(
            model    = self.model_name,
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_content},
            ],
            temperature = 0.1,
        )

        content = completion.choices[0].message.content.strip()

        # Nettoyage si le modèle ajoute des backticks markdown
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {
                "categorie": CATEGORIES[0],
                "urgence":   "Modérée",
                "resume":    content[:300],
            }

        if data.get("categorie") not in CATEGORIES:
            data["categorie"] = CATEGORIES[0]
        if data.get("urgence") not in URGENCES:
            data["urgence"] = "Modérée"
        if not isinstance(data.get("resume"), str):
            data["resume"] = ""

        return data