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
LAT = 43.6
 
 
def j(date, tmin, tmax, precip=0.0, tmoy="auto"):
    return {"id_commune": 1, "date": date, "t_min": tmin, "t_max": tmax,
            "t_moy": (tmin + tmax) / 2 if tmoy == "auto" and tmin is not None else None
                     if tmoy == "auto" else tmoy, "precip": precip}
 
 
def test_gdd_plafond_et_plancher():
    assert gdd_jour(14, 38, 6, 30) == 16.0
    assert gdd_jour(14, 38, 6) == 20.0
    assert gdd_jour(2, 8, 6, 30) == 0.0
 
 
def test_fenetres_de_campagne():
    assert annee_campagne("2000-11-15", (10, 7)) == 2001
    assert annee_campagne("2001-03-01", (10, 7)) == 2001
    assert annee_campagne("2001-08-15", (10, 7)) is None
    assert annee_campagne("2001-06-15", (4, 10)) == 2001
    assert annee_campagne("2001-11-01", (4, 10)) is None
 
 
def test_ra_et_et0_hargreaves():
    assert abs(ra_mm_par_jour(43.6, 196) - 16.6) < 0.4
    assert et0_hargreaves(15, 15, 15, LAT, 196) == 0.0
    et0 = et0_hargreaves(10, 20, 15, LAT, 196)
    assert 3.5 < et0 < 4.5
 
 
def test_gdd_stress_optimale_a_la_main():
    s = [j("2001-06-01", 14, 38),
         j("2001-06-02", 12, 20),
         j("2001-06-03", 20, 35),
         j("2001-06-04", 10, 30)]
    r = indicateurs_horizon(s, MAIS, LAT, 2001, 2001, exiger_campagne_complete=False)
    assert r["gdd_saison_cj"] == 59.0
    assert r["jours_stress_thermique"] == 1.0
    assert r["jours_t_optimale"] == 3.0
    assert r["maturite_atteinte_pct"] == round(100 * 59 / 1600, 1)
    assert r["nb_annees_calculees"] == 1
 
 
def test_gel_seuil_strict_et_moyenne_sur_horizon():
    s = [j("2001-04-01", -1, 10),
         j("2001-04-02", 0.0, 10),
         j("2002-04-01", -1, 10), j("2002-04-02", -2, 10), j("2002-04-03", -0.1, 10)]
    r = indicateurs_horizon(s, MAIS, LAT, 2001, 2002, exiger_campagne_complete=False)
    assert r["jours_gel"] == 2.0
    assert r["nb_annees_calculees"] == 2
 
 
def test_gel_hors_fenetre_ignore():
    s = [j("2001-01-10", -9, 0), j("2001-06-01", 10, 20)]
    assert indicateurs_horizon(s, MAIS, LAT, 2001, 2001, exiger_campagne_complete=False)["jours_gel"] == 0.0
 
 
def test_bilan_hydrique_coherent_avec_et0():
    s = [j("2001-07-15", 10, 20, precip=5.0)]
    attendu = round(5.0 - et0_hargreaves(10, 20, 15, LAT, 196), 1)
    assert indicateurs_horizon(s, MAIS, LAT, 2001, 2001, exiger_campagne_complete=False)["bilan_hydrique_mm"] == attendu
 
 
def test_valeur_manquante_ignoree():
    s = [j("2001-06-01", 14, 38), j("2001-06-02", None, None, tmoy=None)]
    assert indicateurs_horizon(s, MAIS, LAT, 2001, 2001, exiger_campagne_complete=False)["gdd_saison_cj"] == 16.0
 
 
def test_pas_de_gdd_maturite_pour_olivier():
    r = indicateurs_horizon([j("2001-06-01", 20, 30)], OLIVIER, LAT, 2001, 2001, exiger_campagne_complete=False)
    assert r["maturite_atteinte_pct"] is None
 
 
def test_erreurs_explicites():
    for serie, deb, fin in [([j("2001-06-01", 20, 10)], 2001, 2001),
                            ([], 2001, 2001),
                            ([j("2001-06-01", 10, 20)], 1990, 1995)]:
        try:
            indicateurs_horizon(serie, MAIS, LAT, deb, fin, exiger_campagne_complete=False)
            assert False, "une erreur était attendue"
        except ValueError:
            pass
 
 
def _serie_complete(an_debut, an_fin, tmin=5.0, tmax=20.0):
    """Série journalière complète du 1er juillet an_debut-1 au 31 déc. an_fin (valeurs constantes)."""
    import datetime
    d, fin, out = datetime.date(an_debut - 1, 7, 1), datetime.date(an_fin, 12, 31), []
    while d <= fin:
        out.append(j(d.isoformat(), tmin, tmax))
        d += datetime.timedelta(days=1)
    return out
 
 
def test_annee_sans_gel():
    # t_min toujours positive -> 0 jour de gel, et ce n'est pas une erreur
    r = indicateurs_horizon(_serie_complete(2001, 2002), MAIS, LAT, 2001, 2002)
    assert r["jours_gel"] == 0.0 and r["nb_annees_calculees"] == 2
 
 
def test_campagne_incomplete_ignoree():
    # série complète pour 2001 mais qui s'arrête fin juin 2002 : 2002 (maïs, avril-octobre) est incomplète
    s = [x for x in _serie_complete(2001, 2002) if x["date"] <= "2002-06-30"]
    r = indicateurs_horizon(s, MAIS, LAT, 2001, 2002)
    assert r["nb_annees_calculees"] == 1
 
 
def test_campagne_incomplete_debut_blé():
    # blé : la campagne 2002 commence le 1er octobre 2001 ; une série qui démarre en janvier 2002 ne suffit pas
    BLE = {"nom": "Blé tendre hiver", "t_base_c": 0, "gdd_maturite_cj": 2150, "seuil_gel_c": -4,
           "besoin_eau_mm": 500, "t_opt_min_c": 15, "t_opt_max_c": 22, "seuil_stress_thermique_c": 30}
    s = [x for x in _serie_complete(2001, 2002) if x["date"] >= "2002-01-01"]
    try:
        indicateurs_horizon(s, BLE, LAT, 2002, 2002)
        assert False, "une erreur était attendue"
    except ValueError:
        pass
 
 
def test_toutes_campagnes_incompletes_erreur():
    s = [j("2001-06-01", 10, 20)]
    try:
        indicateurs_horizon(s, MAIS, LAT, 2001, 2001)
        assert False, "une erreur était attendue"
    except ValueError:
        pass
 
 
def test_vigne_fenetre_gel_en_mars():
    # vigne : saison avril-octobre mais gel dès mars ; une série qui débute le 1er avril est incomplète
    VIGNE = {"nom": "Vigne (raisin de cuve)", "t_base_c": 10, "gdd_maturite_cj": 1300, "seuil_gel_c": -2,
             "besoin_eau_mm": 400, "t_opt_min_c": 25, "t_opt_max_c": 30, "seuil_stress_thermique_c": 35}
    s = [x for x in _serie_complete(2001, 2001) if x["date"] >= "2001-04-01"]
    try:
        indicateurs_horizon(s, VIGNE, LAT, 2001, 2001)
        assert False, "une erreur était attendue"
    except ValueError:
        pass
 
 
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
    assert fut[901]["gdd_saison_cj"] > ref[901]["gdd_saison_cj"]
    assert fut[901]["jours_gel"] <= ref[901]["jours_gel"]
    assert ref[901]["nb_annees_calculees"] == 3 and fut[901]["nb_annees_calculees"] == 3
 
 
if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("OK ", t.__name__)
    print(f"{len(tests)} tests réussis")
 