# -*- coding: utf-8 -*-
"""
J3.2 (pôle DATA) : calcule les indicateurs du maïs grain pour Lille et Reims
à partir de l'échantillon réel (série au format du contrat), puis GÉNÈRE un
fichier SQL d'INSERT pour fact_indicateur (à exécuter dans phpMyAdmin).

Aucun accès à la base depuis le script : pas d'identifiants à gérer.

Usage (depuis "Dossier Partie DATA") :
    python calculer_gel.py
    python calculer_gel.py "../Dossier Partie DEV/series-reel-MRI_AGCM3_2_S.csv"
"""
import csv
import os
import sys

from indicateurs import ligne_fait

CSV_DEFAUT = os.path.join("..", "Dossier Partie DEV", "series-reel-MRI_AGCM3_2_S.csv")
SORTIE = "insert_fact_indicateur.sql"

# --- Identifiants relevés en base (SELECT du 18/11/2026) -------------------
ID_MODELE = 4                      # MRI_AGCM3_2_S
ID_CULTURE = 4                     # Maïs grain
COMMUNES = {1: ("Lille", 50.63), 4: ("Reims", 49.26)}   # id_commune -> (nom, latitude)
# id_temps -> (début, fin) : l'échantillon (2001-2003 / 2041-2043) est rattaché
# aux décennies 2001-2010 et 2041-2050 ; seules les années présentes sont calculées.
HORIZONS = {8: (2001, 2010), 12: (2041, 2050)}

# --- Culture : valeurs de dim_culture (maïs). À comparer avec la base ! -----
MAIS = {"nom": "Maïs grain", "t_base_c": 6, "gdd_maturite_cj": 1600,
        "seuil_gel_c": 0, "besoin_eau_mm": 600,
        "t_opt_min_c": 20, "t_opt_max_c": 30, "seuil_stress_thermique_c": 35}


def num(x):
    return float(x) if x not in ("", None) else None


def charger(chemin):
    """Séries du contrat : {id_commune: [jours]}."""
    par = {}
    with open(chemin, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cid = int(r["id_commune"])
            par.setdefault(cid, []).append({
                "id_commune": cid, "date": r["date"],
                "t_min": num(r["t_min"]), "t_max": num(r["t_max"]),
                "t_moy": num(r["t_moy"]), "precip": num(r["precip"])})
    return par


def sql_valeur(v):
    return "NULL" if v is None else repr(v) if isinstance(v, (int, float)) else f"'{v}'"


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAUT
    series = charger(chemin)
    lignes_sql = []
    print(f"{'commune':8} {'horizon':10} {'jours_gel':>9} {'GDD':>8} {'stress':>7} {'bilan_h':>8} {'nb_ans':>6}")
    for id_c, (nom, lat) in COMMUNES.items():
        for id_t, (a0, a1) in HORIZONS.items():
            f = ligne_fait(id_c, ID_CULTURE, id_t, ID_MODELE, series[id_c],
                           MAIS, lat, a0, a1)
            print(f"{nom:8} {a0}-{a1:<5} {f['jours_gel']:>9} {f['gdd_saison_cj']:>8} "
                  f"{f['jours_stress_thermique']:>7} {f['bilan_hydrique_mm']:>8} "
                  f"{f['nb_annees_calculees']:>6}")
            cols = list(f)
            maj = ", ".join(f"{c}=VALUES({c})" for c in cols
                            if c not in ("id_commune", "id_culture", "id_temps",
                                         "id_modele", "id_session"))
            lignes_sql.append(
                f"INSERT INTO fact_indicateur ({', '.join(cols)}) VALUES "
                f"({', '.join(sql_valeur(f[c]) for c in cols)}) "
                f"ON DUPLICATE KEY UPDATE {maj};")
    with open(SORTIE, "w", encoding="utf-8") as out:
        out.write("\n".join(lignes_sql) + "\n")
    print(f"\n{len(lignes_sql)} INSERT écrits dans {SORTIE}")


if __name__ == "__main__":
    main()