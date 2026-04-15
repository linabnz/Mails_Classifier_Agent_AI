# comparaison.py
import os
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score

# ----------------------------------------------------------------
# 1. Charger la vérité terrain
# ----------------------------------------------------------------
ground_truth = pd.read_csv("C:\\Users\\Benzemma\\OneDrive\\Bureau\\Classification_mails_agents_IA\\data\\ground_truth (1).csv")
ground_truth = ground_truth[["subjects", "categories", "urgence"]].copy()
ground_truth.columns = ["sujet", "categorie_vraie", "urgence_vraie"]

# ----------------------------------------------------------------
# 2. Charger tous les CSV générés par l'agent
# ----------------------------------------------------------------
DATA_FOLDER = "data"

# Correspondance nom de fichier → nom de catégorie exact
fichiers_categories = {
    "Problème_technique_informatique.csv":       "Problème technique informatique",
    "Demande_administrative.csv":                "Demande administrative",
    "Problème_d_accès__authentification.csv":    "Problème d'accès / authentification",
    "Demande_de_support_utilisateur.csv":        "Demande de support utilisateur",
    "Bug_ou_dysfonctionnement_d_un_service.csv": "Bug ou dysfonctionnement d'un service",
}

all_predicted = []

for filename, categorie in fichiers_categories.items():
    filepath = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df["categorie_predite"] = categorie
        all_predicted.append(df)
        print(f"📄 {filename} → {len(df)} lignes")

predicted = pd.concat(all_predicted, ignore_index=True)
predicted = predicted.rename(columns={
    "Sujet":    "sujet",
    "Urgence":  "urgence_predite",
    "Synthèse": "resume"
})

print(f"\n📊 Total emails prédits : {len(predicted)}")
print(f"📊 Total emails vérité terrain : {len(ground_truth)}")

# ----------------------------------------------------------------
# 3. Fusionner sur le sujet
# ----------------------------------------------------------------
merged = pd.merge(
    ground_truth,
    predicted[["sujet", "categorie_predite", "urgence_predite"]],
    on="sujet",
    how="inner"
)

print(f"✅ Emails matchés : {len(merged)} / {len(ground_truth)}\n")

# ----------------------------------------------------------------
# 4. Précision catégories
# ----------------------------------------------------------------
print("========== PRÉCISION CATÉGORIES ==========")
acc_cat = accuracy_score(merged["categorie_vraie"], merged["categorie_predite"])
print(f"Accuracy : {acc_cat * 100:.1f}%")
print("\nDétail par catégorie :")
print(classification_report(
    merged["categorie_vraie"],
    merged["categorie_predite"],
    zero_division=0
))

# ----------------------------------------------------------------
# 5. Précision urgences
# ----------------------------------------------------------------
print("========== PRÉCISION URGENCES ==========")
acc_urg = accuracy_score(merged["urgence_vraie"], merged["urgence_predite"])
print(f"Accuracy : {acc_urg * 100:.1f}%")
print("\nDétail par niveau d'urgence :")
print(classification_report(
    merged["urgence_vraie"],
    merged["urgence_predite"],
    zero_division=0
))

# ----------------------------------------------------------------
# 6. Sauvegarder les erreurs
# ----------------------------------------------------------------
erreurs_cat = merged[merged["categorie_vraie"] != merged["categorie_predite"]]
erreurs_cat.to_csv("erreurs_categories.csv", index=False)
print(f"❌ Erreurs catégories : {len(erreurs_cat)} → erreurs_categories.csv")

erreurs_urg = merged[merged["urgence_vraie"] != merged["urgence_predite"]]
erreurs_urg.to_csv("erreurs_urgences.csv", index=False)
print(f"❌ Erreurs urgences : {len(erreurs_urg)} → erreurs_urgences.csv")