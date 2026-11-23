# -*- coding: utf-8 -*-
"""
DEV : série climatique complète au format du contrat DEV -> DATA (CONTRAT-INTERFACE.md §2).

S'appuie sur le client du kit (openmeteo_client.py : cache disque + reprise sur 429).
Ce module ajoute ce que décrit conception-DEV.md §3 :
  - paramètres validés AVANT tout appel réseau ;
  - période demandée en tranches de 30 ans (= les 2 horizons de dim_temps), chacune en cache ;
  - lignes concaténées sans doublon de date ;
  - comptage des valeurs manquantes et des jours où t_min > t_max (signalés à DATA).

Début de période : la série démarre le 1er juillet de annee_debut-1 (comme l'échantillon réel
« 01/07/2000-31/12/2003 » du contrat et le docstring du kit), pour couvrir la saison de gel qui
chevauche deux années civiles. Les tranches suivantes démarrent au 1er janvier.
Le contrat décrit `recuperer_serie` (liste de dicts) ; ce module renvoie un dict dont la clé
« lignes » est cette liste : c'est elle qu'on passe à `indicateurs.ligne_fait(..., serie, ...)`.
"""
import logging
import urllib.error

import openmeteo_client as client

log = logging.getLogger(__name__)

COLONNES_MESUREES = ("t_min", "t_max", "t_moy", "precip")
MODELE_PAR_DEFAUT = "MRI_AGCM3_2_S"
DUREE_TRANCHE_ANS = 30
PERIODE_MAX_ANS = 61
ANNEE_MIN, ANNEE_MAX = 1951, 2050          # Open-Meteo Climate : 1950-2050 ; annee_debut-1 doit rester >= 1950
DEBUT_PREMIERE_TRANCHE = "07-01"           # 1er juillet de annee_debut-1
DEBUT_TRANCHE = "01-01"
FIN_TRANCHE = "12-31"


def _valider(id_commune, latitude, longitude, annee_debut, annee_fin, modele):
    """Lève ValueError si un paramètre est invalide (aucun appel réseau n'a eu lieu)."""
    if id_commune is None:
        raise ValueError("id_commune manquant")
    for nom, valeur, bas, haut in (("latitude", latitude, -90, 90), ("longitude", longitude, -180, 180)):
        if isinstance(valeur, bool) or not isinstance(valeur, (int, float)) or not bas <= valeur <= haut:
            raise ValueError(f"{nom} invalide : {valeur!r} (attendu entre {bas} et {haut})")
    for nom, valeur in (("annee_debut", annee_debut), ("annee_fin", annee_fin)):
        if isinstance(valeur, bool) or not isinstance(valeur, int) or not ANNEE_MIN <= valeur <= ANNEE_MAX:
            raise ValueError(f"{nom} invalide : {valeur!r} (attendu entre {ANNEE_MIN} et {ANNEE_MAX})")
    if annee_debut > annee_fin:
        raise ValueError(f"annee_debut ({annee_debut}) > annee_fin ({annee_fin})")
    if annee_fin - annee_debut + 1 > PERIODE_MAX_ANS:
        raise ValueError(f"période trop longue : {annee_fin - annee_debut + 1} ans (maximum {PERIODE_MAX_ANS})")
    if not isinstance(modele, str) or not modele.strip():
        raise ValueError("modèle vide")


def tranches(annee_debut, annee_fin):
    """1991, 2050 -> (1991, 2020), (2021, 2050)."""
    debut = annee_debut
    while debut <= annee_fin:
        fin = min(debut + DUREE_TRANCHE_ANS - 1, annee_fin)
        yield debut, fin
        debut = fin + 1


def recuperer_series(id_commune, latitude, longitude, annee_debut=1991, annee_fin=2050,
                     modele=MODELE_PAR_DEFAUT):
    """Retourne un dict :
        lignes              : liste de {id_commune, date, t_min, t_max, t_moy, precip}, un jour par ligne
        jours_incoherents   : nombre de jours où t_min > t_max (à signaler à DATA)
        valeurs_manquantes  : {colonne: nombre de None}

    Erreurs : ValueError (paramètres), RuntimeError (réponse vide, quota 429 épuisé, API injoignable).
    Les valeurs manquantes restent à None : DATA ignore le jour (precip manquante = 0).
    """
    _valider(id_commune, latitude, longitude, annee_debut, annee_fin, modele)

    lignes, dates_vues = [], set()
    for debut, fin in tranches(annee_debut, annee_fin):
        if debut == annee_debut:
            date_debut = f"{debut - 1}-{DEBUT_PREMIERE_TRANCHE}"
        else:
            date_debut = f"{debut}-{DEBUT_TRANCHE}"
        try:
            serie = client.recuperer_serie(id_commune, latitude, longitude,
                                           date_debut, f"{fin}-{FIN_TRANCHE}", modele)
        except OSError as erreur:       # URLError, HTTPError, délai dépassé
            log.error("API injoignable pour la commune %s, modèle %s, %s-%s : %s",
                      id_commune, modele, debut, fin, erreur)
            raise RuntimeError(f"API Open-Meteo injoignable (commune {id_commune}, "
                               f"{debut}-{fin}) : {erreur}") from erreur
        for ligne in serie:
            if ligne["date"] not in dates_vues:
                dates_vues.add(ligne["date"])
                lignes.append(ligne)

    manquantes = {c: sum(1 for l in lignes if l[c] is None) for c in COLONNES_MESUREES}
    incoherents = sum(1 for l in lignes
                      if l["t_min"] is not None and l["t_max"] is not None and l["t_min"] > l["t_max"])
    return {"lignes": lignes, "jours_incoherents": incoherents, "valeurs_manquantes": manquantes}