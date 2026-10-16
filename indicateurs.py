# -*- coding: utf-8 -*-
"""
Module de calcul des indicateurs agro-climatiques — SAÉ 3.01, pôle DATA (J2).

CONTRAT D'INTERFACE (DEV -> DATA) — une série = une liste de dicts, UN JOUR PAR LIGNE :
    id_commune (int) · date ('YYYY-MM-DD') · t_min · t_max · t_moy (°C) · precip (mm)
    (valeurs manquantes = None)
Une culture = un dict avec les champs de dim_culture (voir referentiel-cultures.csv).
Sortie = un dict dont les clés sont les colonnes de fact_indicateur.

Règles de calcul (justifiées dans le rapport) :
  GDD du jour       = max(0, (t_min + min(t_max, plafond))/2 - t_base)    plafond = 30 °C pour le maïs
                      (DRIAS/ORACLE), sinon pas de plafond ; sans plafond c'est (t_min+t_max)/2.
  jour de gel       = t_min <  seuil_gel_c           (strict, comme la fiche « Comment coder un indicateur »)
  jour de stress    = t_max >  seuil_stress_thermique_c
  jour T° optimale  = t_opt_min_c <= t_moy <= t_opt_max_c
  ET0 (mm/j)        = Hargreaves : 0,0023 × Ra × (t_moy + 17,8) × √(t_max − t_min)
                      (l'API Climate ne fournit PAS ET0 ; Ra = f(latitude, jour), FAO-56)
  bilan hydrique    = Σ (precip − ET0) sur la saison
  agrégation        : valeur par année de campagne, puis MOYENNE sur les années de l'horizon.

Les FENÊTRES (saison de calcul, fenêtre de gel sensible) sont des HYPOTHÈSES D'ÉQUIPE,
regroupées dans PARAMS_CULTURE ci-dessous : faciles à lire, à discuter, à modifier.
"""
import math
from collections import defaultdict

# --------------------------------------------------------------------------
# Hypothèses par culture (clé = nom exact dans dim_culture)
#   saison : (mois_debut, mois_fin) — fenêtre des GDD, du stress, de la T° optimale et du bilan.
#            Si mois_debut > mois_fin, la saison enjambe le nouvel an (ex. blé oct -> juil) et
#            elle est rattachée à l'année de RÉCOLTE.
#   gel    : (mois_debut, mois_fin) — fenêtre où le gel est critique (débourrement, floraison...).
#   plafond_tx : plafond de t_max pour les GDD (None = aucun).
# Sources des fenêtres : DRIAS/ORACLE (blé oct->juil, maïs saison, plafond 30 °C) ;
# les autres sont des choix d'équipe NON SOURCÉS (à valider en J2.4).
# --------------------------------------------------------------------------
DEFAUT = {"saison": (4, 10), "gel": (3, 5), "plafond_tx": None}
PARAMS_CULTURE = {
    "Blé tendre hiver":       {"saison": (10, 7), "gel": (3, 5), "plafond_tx": None},
    "Orge hiver":             {"saison": (10, 7), "gel": (3, 5), "plafond_tx": None},
    "Colza hiver":            {"saison": (8, 7),  "gel": (3, 5), "plafond_tx": None},
    "Maïs grain":             {"saison": (4, 10), "gel": (4, 5), "plafond_tx": 30.0},
    "Vigne (raisin de cuve)": {"saison": (4, 10), "gel": (3, 5), "plafond_tx": None},
}


def params(culture):
    p = dict(DEFAUT)
    p.update(PARAMS_CULTURE.get(culture.get("nom"), {}))
    return p


# --------------------------------------------------------------------------
# Briques élémentaires
# --------------------------------------------------------------------------
def gdd_jour(t_min, t_max, t_base, plafond_tx=None):
    """Degrés-jours de croissance d'une journée (jamais négatif)."""
    tx = min(t_max, plafond_tx) if plafond_tx is not None else t_max
    return max(0.0, (t_min + tx) / 2.0 - t_base)


def ra_mm_par_jour(latitude_deg, jour_annee):
    """Rayonnement extraterrestre Ra en mm/jour (FAO-56, éq. 21) — fiche amorçage DEV."""
    phi = math.radians(latitude_deg)
    dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * jour_annee)
    decl = 0.409 * math.sin(2 * math.pi / 365 * jour_annee - 1.39)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(decl))))
    ra_mj = (24 * 60 / math.pi) * 0.0820 * dr * (
        ws * math.sin(phi) * math.sin(decl) + math.cos(phi) * math.cos(decl) * math.sin(ws))
    return 0.408 * ra_mj


def et0_hargreaves(t_min, t_max, t_moy, latitude_deg, jour_annee):
    """ET0 (mm/jour). Vaut 0 si t_max == t_min (racine nulle)."""
    ecart = max(0.0, t_max - t_min)
    return max(0.0, 0.0023 * ra_mm_par_jour(latitude_deg, jour_annee) * (t_moy + 17.8) * math.sqrt(ecart))


def _parse(date_iso):
    return int(date_iso[0:4]), int(date_iso[5:7]), int(date_iso[8:10])


def _jour_annee(date_iso):
    an, m, j = _parse(date_iso)
    cumul = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    bissextile = (an % 4 == 0 and an % 100 != 0) or an % 400 == 0
    return cumul[m - 1] + j + (1 if bissextile and m > 2 else 0)


def annee_campagne(date_iso, fenetre):
    """Année de campagne si la date est dans la fenêtre (mois_debut, mois_fin), sinon None."""
    an, m, _ = _parse(date_iso)
    d, f = fenetre
    if d <= f:
        return an if d <= m <= f else None
    if m >= d:
        return an + 1          # ex. 15 nov 2000 -> campagne 2001
    if m <= f:
        return an
    return None


# --------------------------------------------------------------------------
# Calcul par année puis par horizon
# --------------------------------------------------------------------------
def indicateurs_annuels(serie, culture, latitude):
    """Retourne {annee_de_campagne: {indicateurs de l'année}}."""
    p = params(culture)
    ann = defaultdict(lambda: {"gdd": 0.0, "gel": 0, "stress": 0, "opt": 0,
                               "pluie": 0.0, "bilan": 0.0, "nb_jours": 0})
    for j in serie:
        if j.get("t_min") is None or j.get("t_max") is None:
            continue                                   # jour inexploitable : ignoré
        if j["t_min"] > j["t_max"]:
            raise ValueError(f"t_min > t_max le {j['date']}")
        t_moy = j["t_moy"] if j.get("t_moy") is not None else (j["t_min"] + j["t_max"]) / 2.0
        pluie = j.get("precip") or 0.0

        a_saison = annee_campagne(j["date"], p["saison"])
        if a_saison is not None:
            a = ann[a_saison]
            a["nb_jours"] += 1
            a["gdd"] += gdd_jour(j["t_min"], j["t_max"], culture["t_base_c"], p["plafond_tx"])
            if j["t_max"] > culture["seuil_stress_thermique_c"]:
                a["stress"] += 1
            if culture["t_opt_min_c"] <= t_moy <= culture["t_opt_max_c"]:
                a["opt"] += 1
            a["pluie"] += pluie
            a["bilan"] += pluie - et0_hargreaves(j["t_min"], j["t_max"], t_moy, latitude,
                                                  _jour_annee(j["date"]))
        a_gel = annee_campagne(j["date"], p["gel"])
        if a_gel is not None and j["t_min"] < culture["seuil_gel_c"]:
            ann[a_gel]["gel"] += 1
    return dict(ann)


def indicateurs_horizon(serie, culture, latitude, annee_debut, annee_fin):
    """Moyenne annuelle sur l'horizon [annee_debut ; annee_fin] -> colonnes de fact_indicateur."""
    annuels = {a: v for a, v in indicateurs_annuels(serie, culture, latitude).items()
               if annee_debut <= a <= annee_fin and v["nb_jours"] > 0}
    if not annuels:
        raise ValueError("aucune année exploitable sur l'horizon demandé")
    n = len(annuels)

    def moy(cle):
        return sum(v[cle] for v in annuels.values()) / n

    gdd = moy("gdd")
    mat = culture.get("gdd_maturite_cj")
    return {
        "gdd_saison_cj": round(gdd, 1),
        "maturite_atteinte_pct": round(100.0 * gdd / mat, 1) if mat else None,
        "jours_gel": round(moy("gel"), 1),
        "jours_stress_thermique": round(moy("stress"), 1),
        "jours_t_optimale": round(moy("opt"), 1),
        "pluie_saison_mm": round(moy("pluie"), 1),
        "bilan_hydrique_mm": round(moy("bilan"), 1),
        "nb_annees_calculees": n,
    }


def ligne_fait(id_commune, id_culture, id_temps, id_modele, serie, culture, latitude,
               annee_debut, annee_fin, id_session="global"):
    """Ligne prête à insérer dans fact_indicateur."""
    return {"id_commune": id_commune, "id_culture": id_culture, "id_temps": id_temps,
            "id_modele": id_modele, "id_session": id_session,
            **indicateurs_horizon(serie, culture, latitude, annee_debut, annee_fin)}


def sql_insert(ligne):
    """INSERT paramétré (valeurs jamais collées dans le texte SQL : anti-injection)."""
    cols = list(ligne)
    sql = (f"INSERT INTO fact_indicateur ({', '.join(cols)}) "
           f"VALUES ({', '.join(['%s'] * len(cols))}) "
           f"ON DUPLICATE KEY UPDATE " + ", ".join(f"{c}=VALUES({c})" for c in cols
                                                    if c not in ("id_commune", "id_culture", "id_temps",
                                                                 "id_modele", "id_session")))
    return sql, [ligne[c] for c in cols]
