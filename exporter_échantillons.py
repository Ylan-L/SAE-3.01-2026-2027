# exporter_echantillon.py : échantillon RÉEL au format du contrat
import csv
from openmeteo_client import _appel_api

MODELE = "MRI_AGCM3_2_S"
IDS = {1, 4}                                   # id_commune : Lille, Reims
PERIODES = [("2000-07-01", "2003-12-31"), ("2040-07-01", "2043-12-31")]
VARS = ["temperature_2m_min", "temperature_2m_max",
        "temperature_2m_mean", "precipitation_sum"]

def col(daily, base):
    """L'API peut suffixer le nom par le modèle (cf. test T2)."""
    for nom in (base, f"{base}_{MODELE}"):
        if nom in daily:
            return daily[nom]
    raise RuntimeError(f"variable absente : {base}")

with open("communes-reference.csv", encoding="utf-8-sig") as f:
    communes = [c for c in csv.DictReader(f, delimiter=";") if int(c["id_commune"]) in IDS]

with open(f"series-reel-{MODELE}.csv", "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["id_commune", "date", "t_min", "t_max", "t_moy", "precip"])
    for c in communes:
        for debut, fin in PERIODES:
            d = _appel_api({"latitude": c["latitude"], "longitude": c["longitude"],
                            "start_date": debut, "end_date": fin,
                            "models": MODELE, "daily": ",".join(VARS)})["daily"]
            tmin, tmax, tmoy, pr = (col(d, v) for v in VARS)
            if all(x is None for x in tmax):
                raise RuntimeError(f"modèle sans données pour la commune {c['id_commune']}")
            for i, jour in enumerate(d["time"]):
                w.writerow([c["id_commune"], jour, tmin[i], tmax[i], tmoy[i], pr[i]])
print("OK")