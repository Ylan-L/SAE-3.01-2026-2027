# -*- coding: utf-8 -*-
"""Jeu d'essais du module indicateurs — résultats attendus CALCULÉS À LA MAIN (commentaires).
Lancer :  python generer_series_test.py && python test_indicateurs.py     (hors-ligne, sans API)
"""
import csv
from indicateurs import (gdd_jour, ra_mm_par_jour, et0_hargreaves, annee_campagne,
                         indicateurs_horizon)

MAIS = {"nom": "Maïs grain", "t_base_c": 6, "gdd_maturite_cj": 1600, "seuil_gel_c": 0,
        "besoin_eau_mm": 600, "t_opt_min_c": 20, "t_opt_max_c": 30, "seuil_stress_thermique_c": 35}
OLIVIER = {"nom": "Olivier", "t_base_c": 10, "gdd_maturite_cj": None, "seuil_gel_c": -8,
           "besoin_eau_mm": 300, "t_opt_min_c": 25, "t_opt_max_c": 32, "seuil_stress_thermique_c": 40}
LAT = 43.6   # Toulouse


def j(date, tmin, tmax, precip=0.0, tmoy="auto"):
    return {"id_commune": 1, "date": date, "t_min": tmin, "t_max": tmax,
            "t_moy": (tmin + tmax) / 2 if tmoy == "auto" and tmin is not None else None
                     if tmoy == "auto" else tmoy, "precip": precip}


# ---- briques --------------------------------------------------------------
def test_gdd_plafond_et_plancher():
    assert gdd_jour(14, 38, 6, 30) == 16.0     # (14+30)/2 - 6  (exemple de la fiche DRIAS)
    assert gdd_jour(14, 38, 6) == 20.0         # sans plafond : (14+38)/2 - 6
    assert gdd_jour(2, 8, 6, 30) == 0.0        # (2+8)/2 - 6 = -1 -> ramené à 0


def test_fenetres_de_campagne():
    assert annee_campagne("2000-11-15", (10, 7)) == 2001   # saison blé, avant le nouvel an
    assert annee_campagne("2001-03-01", (10, 7)) == 2001
    assert annee_campagne("2001-08-15", (10, 7)) is None   # hors saison
    assert annee_campagne("2001-06-15", (4, 10)) == 2001
    assert annee_campagne("2001-11-01", (4, 10)) is None


def test_ra_et_et0_hargreaves():
    assert abs(ra_mm_par_jour(43.6, 196) - 16.6) < 0.4     # valeur donnée par la fiche DEV
    assert et0_hargreaves(15, 15, 15, LAT, 196) == 0.0     # t_max == t_min -> racine nulle
    et0 = et0_hargreaves(10, 20, 15, LAT, 196)             # ≈ 0,0023 × 16,6 × 32,8 × √10 ≈ 3,96
    assert 3.5 < et0 < 4.5


# ---- indicateurs : cas calculés à la main ----------------------------------
def test_gdd_stress_optimale_a_la_main():
    s = [j("2001-06-01", 14, 38),   # gdd 16 · stress (38>35) · tmoy 26 optimale
         j("2001-06-02", 12, 20),   # gdd 10 · pas de stress · tmoy 16 hors optimale
         j("2001-06-03", 20, 35),   # gdd (20+30)/2-6 = 19 · 35>35 FAUX (strict) · tmoy 27,5 optimale
         j("2001-06-04", 10, 30)]   # gdd 14 · tmoy 20 : borne basse INCLUSE -> optimale
    r = indicateurs_horizon(s, MAIS, LAT, 2001, 2001)
    assert r["gdd_saison_cj"] == 59.0              # 16 + 10 + 19 + 14
    assert r["jours_stress_thermique"] == 1.0
    assert r["jours_t_optimale"] == 3.0
    assert r["maturite_atteinte_pct"] == round(100 * 59 / 1600, 1)
    assert r["nb_annees_calculees"] == 1


def test_gel_seuil_strict_et_moyenne_sur_horizon():
    s = [j("2001-04-01", -1, 10),                                   # 2001 : 1 jour de gel
         j("2001-04-02", 0.0, 10),                                  # t_min == seuil -> PAS un gel
         j("2002-04-01", -1, 10), j("2002-04-02", -2, 10), j("2002-04-03", -0.1, 10)]  # 2002 : 3
    r = indicateurs_horizon(s, MAIS, LAT, 2001, 2002)
    assert r["jours_gel"] == 2.0                   # (1 + 3) / 2
    assert r["nb_annees_calculees"] == 2


def test_gel_hors_fenetre_ignore():
    # gel de MAIS compté seulement avril-mai : un gel de janvier ne compte pas
    s = [j("2001-01-10", -9, 0), j("2001-06-01", 10, 20)]
    assert indicateurs_horizon(s, MAIS, LAT, 2001, 2001)["jours_gel"] == 0.0


def test_bilan_hydrique_coherent_avec_et0():
    s = [j("2001-07-15", 10, 20, precip=5.0)]      # 15/07/2001 = jour 196
    attendu = round(5.0 - et0_hargreaves(10, 20, 15, LAT, 196), 1)
    assert indicateurs_horizon(s, MAIS, LAT, 2001, 2001)["bilan_hydrique_mm"] == attendu


# ---- cas limites ------------------------------------------------------------
def test_valeur_manquante_ignoree():
    s = [j("2001-06-01", 14, 38), j("2001-06-02", None, None, tmoy=None)]
    assert indicateurs_horizon(s, MAIS, LAT, 2001, 2001)["gdd_saison_cj"] == 16.0


def test_pas_de_gdd_maturite_pour_olivier():
    r = indicateurs_horizon([j("2001-06-01", 20, 30)], OLIVIER, LAT, 2001, 2001)
    assert r["maturite_atteinte_pct"] is None


def test_erreurs_explicites():
    for serie, deb, fin in [([j("2001-06-01", 20, 10)], 2001, 2001),   # t_min > t_max
                            ([], 2001, 2001),                         # série vide
                            ([j("2001-06-01", 10, 20)], 1990, 1995)]:  # horizon sans données
        try:
            indicateurs_horizon(serie, MAIS, LAT, deb, fin)
            assert False, "une erreur était attendue"
        except ValueError:
            pass


# ---- cohérence physique sur le jeu synthétique ------------------------------
def _charger():
    par = {}
    with open("series_test.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            par.setdefault(int(r["id_commune"]), []).append(
                {"id_commune": int(r["id_commune"]), "date": r["date"], "t_min": float(r["t_min"]),
                 "t_max": float(r["t_max"]), "t_moy": float(r["t_moy"]), "precip": float(r["precip"])})
    return par


def test_sens_physique_sur_jeu_synthetique():
    par = _charger()
    ref = {c: indicateurs_horizon(s, MAIS, 46.0, 2001, 2003) for c, s in par.items()}
    fut = {c: indicateurs_horizon(s, MAIS, 46.0, 2041, 2043) for c, s in par.items()}
    assert ref[903]["gdd_saison_cj"] > ref[902]["gdd_saison_cj"] > ref[901]["gdd_saison_cj"]
    assert fut[901]["gdd_saison_cj"] > ref[901]["gdd_saison_cj"]            # réchauffement -> + de GDD
    assert fut[901]["jours_gel"] <= ref[901]["jours_gel"]                   # ... et pas plus de gel
    assert ref[901]["nb_annees_calculees"] == 3 and fut[901]["nb_annees_calculees"] == 3


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("OK ", t.__name__)
    print(f"{len(tests)} tests réussis")
