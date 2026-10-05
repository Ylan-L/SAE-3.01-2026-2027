# -*- coding: utf-8 -*-
"""
💻 DEV — Client de l'API Open-Meteo Climate (les SÉRIES, via API, non stockées).

VERSION ALLÉGÉE : on ne récupère que la température minimale (suffisant pour
l'indicateur « jours de gel »). Avec mise en cache disque + nouvelle tentative
si l'API limite le débit (HTTP 429).
"""
import os
import json
import time
import hashlib
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = "https://climate-api.open-meteo.com/v1/climate"
# Observations passées (réanalyse ERA5) : sert à vérifier qu'un modèle est plausible
# sur une période où l'on sait ce qui s'est réellement passé.
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cache")

# 🔑 CLÉ API (facultative). Sans clé : API gratuite, limitée à 10 000 appels par jour
#    et PAR ADRESSE IP — toute la salle partage la même. Avec la clé fournie sur Moodle :
#    serveurs réservés (adresses préfixées « customer- »), sans cette limite par IP.
#    La clé se range dans le fichier .env, à côté de ce script :
#        OPENMETEO_API_KEY=la_cle_fournie_sur_moodle
#    JAMAIS dans le code : .env est exclu de Git par le .gitignore du kit.
#    Si la clé est absente, invalide ou expirée, le client repasse tout seul sur l'API
#    gratuite : l'application continue de fonctionner.
DOSSIER = os.path.dirname(os.path.abspath(__file__))


def _lire_cle():
    """La clé vient de l'environnement, sinon du fichier .env du kit (sans dépendance)."""
    cle = os.environ.get("OPENMETEO_API_KEY", "").strip()
    chemin = os.path.join(DOSSIER, ".env")
    if not cle and os.path.exists(chemin):
        with open(chemin, encoding="utf-8-sig") as f:
            for ligne in f:
                nom, _, valeur = ligne.partition("=")
                if nom.strip() == "OPENMETEO_API_KEY":
                    cle = valeur.strip().strip("\"'")
    return cle or None


API_KEY = _lire_cle()


def _url_client(base_url):
    """https://climate-api.open-meteo.com/… → https://customer-climate-api.open-meteo.com/…"""
    return base_url.replace("https://", "https://customer-", 1)


def _refus_de_cle(erreur):
    """Vrai si l'API refuse la CLÉ (invalide, expirée) — et non les paramètres."""
    if erreur.code not in (400, 401, 403):
        return False
    try:
        raison = json.loads(erreur.read().decode("utf-8")).get("reason", "")
    except Exception:
        return False
    return "api key" in raison.lower()

# ⚠️ Open-Meteo applique PAR DÉFAUT une correction de biais (recalage sur ERA5-Land).
#    Ne passez jamais disable_bias_correction=true : vos modèles ne seraient plus
#    comparables entre eux, ni avec la réalité.


def _chemin_cache(params, base_url=BASE_URL):
    empreinte = dict(params)
    if base_url != BASE_URL:            # l'URL n'entre dans la clé que si elle change :
        empreinte["_url"] = base_url    # les caches déjà constitués restent valables
    cle = hashlib.md5(json.dumps(empreinte, sort_keys=True).encode()).hexdigest()
    return os.path.join(CACHE_DIR, cle + ".json")


def en_cache(params, base_url=BASE_URL):
    """Vrai si la réponse est déjà sur le disque : l'appel ne coûtera rien au quota."""
    return os.path.exists(_chemin_cache(params, base_url))


def _appel_api(params, base_url=BASE_URL):
    """Appelle l'API (avec cache disque + retry sur 429).
    La clé n'entre PAS dans la clé du cache : même réponse avec ou sans clé."""
    global API_KEY
    os.makedirs(CACHE_DIR, exist_ok=True)
    chemin = _chemin_cache(params, base_url)
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)

    for attente in (0, 5, 15, 30):                 # patiente puis réessaie si 429
        if attente:
            time.sleep(attente)
        if API_KEY:
            url = _url_client(base_url) + "?" + urllib.parse.urlencode({**params, "apikey": API_KEY})
        else:
            url = base_url + "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=60) as rep:
                donnees = json.load(rep)
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(donnees, f)
            return donnees
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue
            if API_KEY and _refus_de_cle(e):
                print("[ATTENTION] Clé Open-Meteo refusée (invalide ou expirée) : retour à l'API gratuite.")
                API_KEY = None                     # une seule fois : les appels suivants suivent
                return _appel_api(params, base_url)
            raise
    raise RuntimeError("API Open-Meteo : trop de requêtes (429). Réessayez plus tard.")


def recuperer_tmin(latitude, longitude, date_debut, date_fin, modele="MRI_AGCM3_2_S"):
    """Retourne { 'date': [...], 't_min': [...] } pour la période demandée."""
    params = {
        "latitude": latitude, "longitude": longitude,
        "start_date": date_debut, "end_date": date_fin,
        "models": modele, "daily": "temperature_2m_min",
    }
    daily = (_appel_api(params).get("daily") or {})
    if not daily.get("time"):
        raise RuntimeError("Réponse vide de l'API (vérifier le modèle / la période).")
    return {"date": daily["time"], "t_min": daily.get("temperature_2m_min", [])}


if __name__ == "__main__":
    print("Clé API :", "trouvée → serveurs réservés" if API_KEY else "absente → API gratuite")
    c = recuperer_tmin(43.60, 1.44, "2019-01-01", "2019-12-31")
    print("Jours récupérés :", len(c["date"]), "| ex :", c["date"][0], c["t_min"][0], "°C")