# -*- coding: utf-8 -*-
"""T9 (manuel) : un vrai appel à l'API pour 1 commune (Lille) et 1 an, modèle MRI_AGCM3_2_S.
Vérifie le format du contrat et note le taux de valeurs manquantes."""
from series_contrat import recuperer_series

COLONNES = ["id_commune", "date", "t_min", "t_max", "t_moy", "precip"]

res = recuperer_series(1, 50.63, 3.06, 2020, 2020)
lignes = res["lignes"]

print("Jours récupérés :", len(lignes), "| de", lignes[0]["date"], "à", lignes[-1]["date"])
print("Première ligne  :", lignes[0])
print("Colonnes conformes au contrat :", all(list(l.keys()) == COLONNES for l in lignes))
print("Dates uniques   :", len({l["date"] for l in lignes}) == len(lignes))
print("Jours t_min > t_max :", res["jours_incoherents"])
for colonne, n in res["valeurs_manquantes"].items():
    print(f"Manquants {colonne:7}: {n} ({100 * n / len(lignes):.1f} %)")
