# -*- coding: utf-8 -*-
"""Tests hors ligne de series_contrat.py (T1 à T5 du plan de tests) : aucun appel réseau.
Lancer :  python -m unittest -v test_series_contrat
"""
import unittest
import urllib.error
from unittest import mock

import series_contrat as sc

COLONNES_CONTRAT = ["id_commune", "date", "t_min", "t_max", "t_moy", "precip"]


def ligne(date, t_min=1.0, t_max=5.0, t_moy=3.0, precip=0.0, id_commune=1):
    return {"id_commune": id_commune, "date": date,
            "t_min": t_min, "t_max": t_max, "t_moy": t_moy, "precip": precip}


def deux_jours_par_tranche(id_commune, lat, lon, debut, fin, modele):
    """Faux client : une ligne au début et une à la fin de la tranche demandée."""
    return [ligne(debut, id_commune=id_commune), ligne(fin, id_commune=id_commune)]


def avec_faux_client(**kw):
    return mock.patch.object(sc.client, "recuperer_serie", **kw)


class TestT1FormatContrat(unittest.TestCase):
    def test_colonnes_dans_l_ordre_et_valeurs_manquantes_comptees(self):
        reponse = [ligne("2020-01-01"),
                   ligne("2020-01-02", t_min=None, precip=None),
                   ligne("2020-01-03", t_max=None, t_moy=None, precip=None)]
        with avec_faux_client(return_value=reponse):
            r = sc.recuperer_series(1, 50.63, 3.06, 2020, 2020)
        self.assertEqual(list(r["lignes"][0].keys()), COLONNES_CONTRAT)
        self.assertEqual(len(r["lignes"]), 3)
        self.assertEqual(r["valeurs_manquantes"], {"t_min": 1, "t_max": 1, "t_moy": 1, "precip": 2})
        self.assertEqual(r["jours_incoherents"], 0)


class TestT2SerieEntiere(unittest.TestCase):
    def test_deux_appels_de_30_ans(self):
        with avec_faux_client(side_effect=deux_jours_par_tranche) as faux:
            r = sc.recuperer_series(1, 50.63, 3.06, 1991, 2050)
        self.assertEqual(faux.call_count, 2)
        periodes = [(c.args[3], c.args[4]) for c in faux.call_args_list]
        # la 1re tranche démarre le 1er juillet de annee_debut-1 (saison de gel à cheval sur 2 années)
        self.assertEqual(periodes, [("1990-07-01", "2020-12-31"), ("2021-01-01", "2050-12-31")])
        self.assertEqual([l["date"] for l in r["lignes"]],
                         ["1990-07-01", "2020-12-31", "2021-01-01", "2050-12-31"])

    def test_une_annee_commence_le_1er_juillet_precedent(self):
        with avec_faux_client(side_effect=deux_jours_par_tranche) as faux:
            sc.recuperer_series(1, 50.63, 3.06, 2001, 2003)
        self.assertEqual([(c.args[3], c.args[4]) for c in faux.call_args_list],
                         [("2000-07-01", "2003-12-31")])

    def test_modele_transmis_au_client(self):
        with avec_faux_client(side_effect=deux_jours_par_tranche) as faux:
            sc.recuperer_series(1, 50.63, 3.06, 1991, 2050, modele="CMCC_CM2_VHR4")
        self.assertTrue(all(c.args[5] == "CMCC_CM2_VHR4" for c in faux.call_args_list))

    def test_doublons_supprimes_entre_tranches(self):
        reponses = [[ligne("2020-12-31"), ligne("2020-12-30")],
                    [ligne("2020-12-31"), ligne("2021-01-01")]]       # 2020-12-31 revient
        with avec_faux_client(side_effect=reponses):
            r = sc.recuperer_series(1, 50.63, 3.06, 1991, 2050)
        self.assertEqual([l["date"] for l in r["lignes"]], ["2020-12-31", "2020-12-30", "2021-01-01"])

    def test_une_seule_annee_un_seul_appel(self):
        with avec_faux_client(side_effect=deux_jours_par_tranche) as faux:
            sc.recuperer_series(1, 50.63, 3.06, 2020, 2020)
        self.assertEqual(faux.call_count, 1)

    def test_tranches(self):
        self.assertEqual(list(sc.tranches(1991, 2050)), [(1991, 2020), (2021, 2050)])
        self.assertEqual(list(sc.tranches(2000, 2035)), [(2000, 2029), (2030, 2035)])


class TestT3ReponsesInexploitables(unittest.TestCase):
    def test_reponse_vide_remonte_en_runtimeerror(self):
        with avec_faux_client(side_effect=RuntimeError("Réponse vide de l'API")):
            with self.assertRaises(RuntimeError):
                sc.recuperer_series(1, 50.63, 3.06, 1991, 2050)

    def test_api_injoignable_journalisee_puis_runtimeerror(self):
        with avec_faux_client(side_effect=urllib.error.URLError("pas de réseau")):
            with self.assertLogs("series_contrat", level="ERROR"):
                with self.assertRaises(RuntimeError):
                    sc.recuperer_series(1, 50.63, 3.06, 1991, 2050)


class TestT4ParametresInvalides(unittest.TestCase):
    """Chaque cas doit être refusé SANS aucun appel au client."""
    CAS = {
        "latitude trop grande": dict(latitude=91, longitude=3.06),
        "latitude texte": dict(latitude="50.6", longitude=3.06),
        "latitude NaN": dict(latitude=float("nan"), longitude=3.06),
        "longitude trop petite": dict(latitude=50.63, longitude=-181),
        "annee_debut hors bornes": dict(latitude=50.63, longitude=3.06, annee_debut=1900),
        "annee_debut 1950 (juillet 1949 hors API)": dict(latitude=50.63, longitude=3.06,
                                                         annee_debut=1950, annee_fin=2000),
        "annee_fin hors bornes": dict(latitude=50.63, longitude=3.06, annee_fin=2051),
        "bornes inversées": dict(latitude=50.63, longitude=3.06, annee_debut=2040, annee_fin=2030),
        "période de plus de 61 ans": dict(latitude=50.63, longitude=3.06, annee_debut=1950, annee_fin=2050),
        "modèle vide": dict(latitude=50.63, longitude=3.06, modele=""),
        "modèle espaces": dict(latitude=50.63, longitude=3.06, modele="   "),
        "id_commune absent": dict(id_commune=None, latitude=50.63, longitude=3.06),
    }

    def test_refus_sans_appel_reseau(self):
        for nom, params in self.CAS.items():
            with self.subTest(nom):
                params = {"id_commune": 1, "annee_debut": 1991, "annee_fin": 2050, **params}
                with avec_faux_client() as faux:
                    with self.assertRaises(ValueError):
                        sc.recuperer_series(**params)
                    faux.assert_not_called()

    def test_periode_de_61_ans_acceptee(self):
        with avec_faux_client(side_effect=deux_jours_par_tranche):
            sc.recuperer_series(1, 50.63, 3.06, 1990, 2050)


class TestT5Incoherences(unittest.TestCase):
    def test_t_min_superieur_a_t_max_compte(self):
        reponse = [ligne("2020-01-01", t_min=8.0, t_max=5.0),     # incohérent
                   ligne("2020-01-02", t_min=5.0, t_max=5.0),     # égal : valide
                   ligne("2020-01-03", t_min=None, t_max=5.0),    # manquant : non compté
                   ligne("2020-01-04", t_min=9.0, t_max=2.0)]     # incohérent
        with avec_faux_client(return_value=reponse):
            r = sc.recuperer_series(1, 50.63, 3.06, 2020, 2020)
        self.assertEqual(r["jours_incoherents"], 2)
        self.assertEqual(len(r["lignes"]), 4)       # les jours incohérents ne sont pas supprimés


if __name__ == "__main__":
    unittest.main()