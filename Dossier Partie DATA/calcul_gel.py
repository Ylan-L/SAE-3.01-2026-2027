# -*- coding: utf-8 -*-
"""
J3.2 (pôle DATA) : calcule les indicateurs du maïs grain pour Lille et Reims
et les ÉCRIT DIRECTEMENT dans fact_indicateur (base bddsae_agri sur AlwaysData).

Lit dans la base : les séries (serie_climat), la culture (dim_culture) et la
latitude des communes (dim_commune) -> plus aucune valeur recopiée à la main.

Prérequis :  pip install pymysql python-dotenv
Identifiants de la base de données : dans le fichier .env 

Usage (depuis "Dossier Partie DATA") :  python calculer_gel.py
"""
import os
import sys

import pymysql
from dotenv import load_dotenv

from indicateurs import ligne_fait, sql_insert

load_dotenv()                                   # lit .env 

# --- Identifiants relevés en base (SELECT du 18/11/2026) -------------------
ID_MODELE = 4                                   # MRI_AGCM3_2_S
ID_CULTURE = 4                                  # Maïs grain
IDS_COMMUNES = (1, 4)                           # Lille, Reims
# id_temps -> (début, fin). L'échantillon (2001-2003 / 2041-2043) est rattaché aux
# décennies 2001-2010 et 2041-2050 ; seules les années présentes sont calculées.
HORIZONS = {8: (2001, 2010), 12: (2041, 2050)}


def en_float(ligne):
    """MariaDB renvoie des Decimal : on les convertit pour éviter une TypeError."""
    return {k: (float(v) if hasattr(v, "as_tuple") else v) for k, v in ligne.items()}


def connexion():
    manquants = [v for v in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
                 if not os.environ.get(v)]
    if manquants:
        sys.exit(f"Variables absentes du .env : {', '.join(manquants)}")
    return pymysql.connect(host=os.environ["DB_HOST"], database=os.environ["DB_NAME"],
                           user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
                           charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)


def main():
    con = connexion()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM dim_culture WHERE id_culture = %s", (ID_CULTURE,))
        culture = en_float(cur.fetchone())

        print(f"{'commune':8} {'horizon':10} {'jours_gel':>9} {'GDD':>8} {'stress':>7} "
              f"{'bilan_h':>8} {'nb_ans':>6}")
        for id_c in IDS_COMMUNES:
            cur.execute("SELECT nom_commune, latitude FROM dim_commune WHERE id_commune = %s",
                        (id_c,))
            c = en_float(cur.fetchone())
            cur.execute("SELECT id_commune, date, t_min, t_max, t_moy, precip "
                        "FROM serie_climat WHERE id_commune = %s ORDER BY date", (id_c,))
            serie = []
            for r in cur.fetchall():
                r = en_float(r)
                r["date"] = r["date"].isoformat()      # contrat : 'YYYY-MM-DD'
                serie.append(r)

            for id_t, (a0, a1) in HORIZONS.items():
                f = ligne_fait(id_c, ID_CULTURE, id_t, ID_MODELE, serie,
                               culture, c["latitude"], a0, a1)
                sql, params = sql_insert(f)            # INSERT paramétré (anti-injection)
                cur.execute(sql, params)
                print(f"{c['nom_commune']:8} {a0}-{a1:<5} {f['jours_gel']:>9} "
                      f"{f['gdd_saison_cj']:>8} {f['jours_stress_thermique']:>7} "
                      f"{f['bilan_hydrique_mm']:>8} {f['nb_annees_calculees']:>6}")
    con.commit()
    con.close()
    print("\nFaits écrits dans fact_indicateur.")


if __name__ == "__main__":
    main()