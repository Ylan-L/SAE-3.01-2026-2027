# -*- coding: utf-8 -*-
"""Tests hors ligne du client Open-Meteo : aucun appel réseau, aucune clé nécessaire.
Lancer depuis le dossier du client :  python -m unittest -v test_openmeteo_client
"""
import io
import json
import tempfile
import unittest
import urllib.error
from unittest import mock

import openmeteo_client as client

COLONNES_CONTRAT = ["id_commune", "date", "t_min", "t_max", "t_moy", "precip"]

PARAMS = {
    "latitude": 50.63, "longitude": 3.06,
    "start_date": "2020-07-01", "end_date": "2020-07-03",
    "models": "MRI_AGCM3_2_S", "daily": "temperature_2m_min",
}
DONNEES = {"daily": {"time": ["2020-07-01"], "temperature_2m_min": [10.0]}}


def reponse_http(donnees):
    """Fausse réponse d'urlopen : un flux lisible par json.load, utilisable avec « with »."""
    return io.BytesIO(json.dumps(donnees).encode("utf-8"))


def erreur_http(code):
    return urllib.error.HTTPError("https://exemple.test", code, "erreur simulée", {}, None)


class TestFormatContrat(unittest.TestCase):
    """T1 : 6 colonnes dans l'ordre, valeurs manquantes laissées à None."""

    def serie(self, daily):
        with mock.patch.object(client, "_appel_api", return_value={"daily": daily}):
            return client.recuperer_serie(7, 50.63, 3.06, "2020-07-01", "2020-07-03")

    def test_colonnes_et_valeurs_exactes(self):
        s = self.serie({
            "time": ["2020-07-01", "2020-07-02", "2020-07-03"],
            "temperature_2m_min": [12.1, None, 11.0],
            "temperature_2m_max": [24.0, 25.5, 23.2],
            "temperature_2m_mean": [18.0, 19.1, 17.4],
            "precipitation_sum": [0.0, 1.2, None],
        })
        self.assertEqual(len(s), 3)
        self.assertEqual(list(s[0].keys()), COLONNES_CONTRAT)
        self.assertEqual(s[0], {"id_commune": 7, "date": "2020-07-01",
                                "t_min": 12.1, "t_max": 24.0, "t_moy": 18.0, "precip": 0.0})
        self.assertIsNone(s[1]["t_min"])
        self.assertIsNone(s[2]["precip"])
        self.assertEqual([l["date"] for l in s], ["2020-07-01", "2020-07-02", "2020-07-03"])

    def test_variable_absente_donne_des_none(self):
        s = self.serie({"time": ["2020-07-01", "2020-07-02"],
                        "temperature_2m_min": [1.0, 2.0], "temperature_2m_max": [5.0, 6.0],
                        "temperature_2m_mean": [3.0, 4.0]})
        self.assertEqual(len(s), 2)
        self.assertTrue(all(l["precip"] is None for l in s))
        self.assertEqual([l["t_min"] for l in s], [1.0, 2.0])

    def test_longueur_incoherente_donne_des_none(self):
        s = self.serie({"time": ["2020-07-01", "2020-07-02", "2020-07-03"],
                        "temperature_2m_min": [1.0, 2.0, 3.0], "temperature_2m_max": [5.0, 6.0, 7.0],
                        "temperature_2m_mean": [3.0, 4.0, 5.0],
                        "precipitation_sum": [0.0, 1.0]})
        self.assertEqual(len(s), 3)
        self.assertTrue(all(l["precip"] is None for l in s))


class TestReponsesVides(unittest.TestCase):
    """T3 : réponse vide -> RuntimeError."""

    def test_reponses_vides(self):
        for reponse in ({}, {"daily": {}}, {"daily": {"time": []}}):
            with self.subTest(reponse=reponse):
                with mock.patch.object(client, "_appel_api", return_value=reponse):
                    with self.assertRaises(RuntimeError):
                        client.recuperer_serie(1, 50.63, 3.06, "2020-07-01", "2020-07-03")
                    with self.assertRaises(RuntimeError):
                        client.recuperer_tmin(50.63, 3.06, "2020-07-01", "2020-07-03")


class _Isole(unittest.TestCase):
    """Cache dans un dossier temporaire, pas de clé API, pas de vraie pause."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        for p in (mock.patch.object(client, "CACHE_DIR", tmp.name),
                  mock.patch.object(client, "API_KEY", None)):
            p.start()
            self.addCleanup(p.stop)


class TestCache(_Isole):
    """T7 : même requête deux fois -> un seul appel réseau."""

    def test_meme_requete_un_seul_appel(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=lambda url, timeout=60: reponse_http(DONNEES)) as urlopen:
            self.assertFalse(client.en_cache(PARAMS))
            premier = client._appel_api(PARAMS)
            second = client._appel_api(PARAMS)
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(premier, second)
        self.assertTrue(client.en_cache(PARAMS))

    def test_requete_differente_nouvel_appel(self):
        autre = {**PARAMS, "end_date": "2020-07-10"}
        with mock.patch("urllib.request.urlopen",
                        side_effect=lambda url, timeout=60: reponse_http(DONNEES)) as urlopen:
            client._appel_api(PARAMS)
            client._appel_api(autre)
        self.assertEqual(urlopen.call_count, 2)


class TestQuota429(_Isole):
    """T8 : 429 -> 4 tentatives espacées, puis arrêt propre (RuntimeError)."""

    def test_arret_propre_apres_4_tentatives(self):
        with mock.patch("urllib.request.urlopen", side_effect=erreur_http(429)) as urlopen, \
             mock.patch("time.sleep") as pause:
            with self.assertRaises(RuntimeError):
                client._appel_api(PARAMS)
        self.assertEqual(urlopen.call_count, 4)
        self.assertEqual([c.args[0] for c in pause.call_args_list], [5, 15, 30])
        self.assertFalse(client.en_cache(PARAMS))

    def test_reprise_apres_un_429(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=[erreur_http(429), reponse_http(DONNEES)]) as urlopen, \
             mock.patch("time.sleep"):
            resultat = client._appel_api(PARAMS)
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(resultat, DONNEES)

    def test_autre_erreur_http_remonte_sans_retry(self):
        with mock.patch("urllib.request.urlopen", side_effect=erreur_http(500)) as urlopen, \
             mock.patch("time.sleep"):
            with self.assertRaises(urllib.error.HTTPError):
                client._appel_api(PARAMS)
        self.assertEqual(urlopen.call_count, 1)


if __name__ == "__main__":
    unittest.main()