import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()                                  # lit le fichier .env
CLE = os.environ.get("OPENMETEO_API_KEY")      # ta clé (ou None)

URL_GRATUIT = "https://climate-api.open-meteo.com/v1/climate"
URL_AVEC_CLE = "https://customer-climate-api.open-meteo.com/v1/climate"


def nom_fichier_cache(params):
    """Un nom de fichier unique pour chaque combinaison de paramètres."""
    texte = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
    return "cache_" + str(abs(hash(texte))) + ".json"


def recuperer_climat(lat, lon, modele, debut, fin, variables):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": debut,
        "end_date": fin,
        "models": modele,
        "daily": ",".join(variables),
        "timezone": "Europe/Paris",
    }

    # Si on a déjà cette réponse, on la relit au lieu de rappeler l'API
    fichier = nom_fichier_cache(params)
    if os.path.exists(fichier):
        with open(fichier, encoding="utf-8") as f:
            return json.load(f)["daily"]

    #  Sinon on appelle l'API (avec la clé si on l'a)
    url = URL_GRATUIT
    if CLE:
        url = URL_AVEC_CLE
        params["apikey"] = CLE

    reponse = requests.get(url, params=params, timeout=15)

    #  On vérifie que ça a marché
    if reponse.status_code != 200:
        raise RuntimeError(f"Erreur {reponse.status_code} : {reponse.text}")

    data = reponse.json()

    #  On sauvegarde pour la prochaine fois
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f)

    return data["daily"]

if __name__ == "__main__":
    if CLE:
        print("Clé API : trouvée")
    else:
        print("Clé API : absente (repli sur l'API gratuite)")