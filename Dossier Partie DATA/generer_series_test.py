# -*- coding: utf-8 -*-
"""Génère series_test.csv au FORMAT DU CONTRAT : id_commune,date,t_min,t_max,t_moy,precip.
Séries SYNTHÉTIQUES déterministes (aucune donnée réelle, aucun aléa) :
  commune 901 = froide (T° moy. 6 °C) · 902 = tempérée (11 °C) · 903 = chaude (16 °C)
  deux horizons : 2001-2003 (référence) et 2041-2043 (+2 °C) -> sert à vérifier le SENS du changement.
Usage :  python generer_series_test.py
"""
import csv
import math
from datetime import date, timedelta

COMMUNES = {901: 6.0, 902: 11.0, 903: 16.0}
PERIODES = {(2001, 2003): 0.0, (2041, 2043): 2.0}   # (début, fin) 


def jour(moy, d):
    saison = -math.cos(2 * math.pi * (d.timetuple().tm_yday - 15) / 365.0)  # ~-1 janvier, +1 juillet
    t = moy + 9.0 * saison
    return round(t - 5.0, 1), round(t + 5.0, 1), round(t, 1)               


with open("series_test.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id_commune", "date", "t_min", "t_max", "t_moy", "precip"])
    for cid, moy in COMMUNES.items():
        for (a0, a1), plus in PERIODES.items():
            d = date(a0 - 1, 7, 1)                  
            fin = date(a1, 12, 31)
            while d <= fin:
                tmin, tmax, tmoy = jour(moy + plus, d)
                w.writerow([cid, d.isoformat(), tmin, tmax, tmoy, 3.0 if d.day % 4 == 0 else 0.0])
                d += timedelta(days=1)
print("series_test.csv généré")
