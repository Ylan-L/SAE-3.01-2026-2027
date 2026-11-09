# 🌾 AgriFutur — Climat & Cultures (SAÉ 3.01)

> **Comment le climat de ma commune va-t-il évoluer d'ici 2050, et quelles cultures y resteront viables ?**

Application web qui transforme des **projections climatiques** en **indicateurs agro-climatiques** compréhensibles et actionnables, à l'échelle d'une commune. Projet réalisé dans le cadre de la SAÉ 3.01 du BUT Informatique 2 (IUT de Créteil-Vitry, Université Paris-Est Créteil), année 2026-2027, inspiré de la démarche AgroClimat2050.

⚠️ Il s'agit de **projections, pas de prévisions** : l'application affiche des fourchettes et l'incertitude entre modèles, jamais un chiffre unique présenté comme une certitude.

---

## 🎯 Fonctionnalités

- Choisir une **commune** (16 communes de référence), une **culture** (10 cultures sourcées) et un **horizon** (aujourd'hui → 2050)
- Obtenir un **verdict** : Viable / À risque / Non viable
- Consulter des **indicateurs** : jours de gel, stress thermique, bilan hydrique, sommes de températures (GDD)
- **Comparer** plusieurs modèles climatiques pour visualiser l'incertitude
- Voir l'évolution du climat de 1950 à 2050 et le décalage des zones de culture
- Compte utilisateur facultatif (favoris), conforme au RGPD

## 🧱 Architecture

```
Open-Meteo Climate API ──(séries brutes, non stockées)──┐
                                                        ▼
                                          Calcul des indicateurs (Python)
                                                        │
   Dim_Culture · Dim_Commune · Dim_Temps · Dim_Modele ──┤
                                                        ▼
                                              Fact_Indicateur  (stockée)
                                                        │
                                                        ▼
                                                 Application web
```

- **Schéma en étoile** (datamart) : 4 dimensions + 1 table de faits `fact_indicateur` (granularité commune × culture × horizon × modèle)
- Les **séries climatiques brutes** sont récupérées côté back-end via l'API Open-Meteo (avec cache et gestion des erreurs), utilisées pour le calcul, puis non conservées
- **Contrat d'interface** DEV ↔ DATA : voir [`CONTRAT-INTERFACE.md`](CONTRAT-INTERFACE.md)
- Le pôle **DEV** produit les séries, le pôle **DATA** produit les faits

## 🛠️ Technologies

| Domaine | Choix |
|---|---|
| Back-end | Python (Flask) |
| Front-end | HTML / CSS (maquette), intégration en cours |
| Base de données | MariaDB sur AlwaysData |
| Données climatiques | [Open-Meteo Climate API](https://open-meteo.com/en/docs/climate-api) (CMIP6, ~10 km) |
| Hébergement | AlwaysData |
| Versionnage | Git / GitHub |

## 📁 Structure du dépôt

| Élément | Contenu |
|---|---|
| `Dossier Partie DATA/` | Scripts SQL (création et chargement), référentiel cultures/communes, module de calcul `indicateurs.py`, jeux d'essais et tests |
| `Dossier Partie DEV/` | Maquette IHM (HTML/CSS), client API Open-Meteo, squelette de l'application |
| `Fichiers .md/` | Documents de suivi (cahier de suivi, journal d'usage de l'IA…) |
| `CONTRAT-INTERFACE.md` | Format d'échange entre les pôles DEV et DATA |
| `17-poc-empreinte-ia.py` | Estimation de l'empreinte environnementale de l'usage de l'IA |
| `Trace Ecrite Commun SAE3.01.pdf` | Analyse du besoin, personas, backlog MoSCoW |

## 🚀 Lancer le projet en local

```bash
# 1. Cloner le dépôt
git clone https://github.com/Ylan-L/SAE-3.01-2026-2027.git
cd SAE-3.01-2026-2027

# 2. Créer un environnement virtuel et installer les dépendances
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Tester le module de calcul des indicateurs, hors-ligne et sans API :

```bash
python generer_series_test.py
python test_indicateurs.py
```

> Les chemins exacts dépendent de l'emplacement des fichiers dans les dossiers `Partie DATA` / `Partie DEV`.

## 📅 Avancement

| Jalon | Semaines | Contenu | État |
|---|---|---|---|
| J0 | S38 | Lancement, dépôt Git, hello world déployé | Fait |
| J1 | S39–S40 | Analyse, personas, backlog, premiers tests API | Fait |
| J2 | S41–S45 | Conception : modèle en étoile, BDD, indicateurs, maquettes | Fait |
| J3 | S46–S48 | MVP : client API + calcul + affichage de bout en bout | En cours |
| J4 | S49–S51 | Enrichissement : indicateurs, incertitude, RGPD | En cours |
| J5 | S01–S03 | Mise en production, rapport, soutenance | En cours |

Chaque jalon est publié dans l'onglet **Releases** (tags `Jalon-1`, `Jalon-2`…).

## Usage de l'IA

L'IA est utilisée comme copilote, jamais comme source. Tout usage significatif est tracé dans `JOURNAL-IA.md` et son empreinte environnementale est estimée avec `17-poc-empreinte-ia.py`. Les clés d'API ne sont jamais versionnées (`.env` est dans le `.gitignore`).

## 👥 Équipe (groupe 5)

| Membre | Pôle |
|---|---|
| Adam Murdakhaiev | DATA |
| Nabil Merzouk | DATA |
| Samuel Mihaila | DEV |
| Ylan Leang | DATA |
| Adrien Garrigon-Viramoutou | DEV |
| Thenujan Nanthakumar | DEV |

## 📚 Sources

- [Open-Meteo Climate API](https://open-meteo.com/en/docs/climate-api)
- [DRIAS – Météo-France](https://www.drias-climat.fr/)
- Seuils agronomiques : ECOCROP, FAO-56, Arvalis, instituts techniques (sources citées dans `dim_culture`)

---

*SAÉ 3.01 « Climat & Cultures » — BUT Informatique 2 — IUT de Créteil-Vitry, UPEC — 2026-2027*
