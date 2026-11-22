# Contrat d'interface DEV ↔ DATA — « Climat & Cultures »
 
**Version :** 1.0 — **Date :** 20/11/2026 — **Statut :** validé par les pôles DEV et DATA
 
**Historique :**
- v1.0 (20/11/2026) : première version versionnée. Format vérifié sur l'échantillon réel (5 116 lignes). Toute modification du format passe à 1.1 (compatible) ou 2.0 (qui casse la compatibilité), avec une ligne ici.
---
 
## 1. En une image
 
```
Open-Meteo ──► [DEV] client API ──► SÉRIE (1 jour = 1 ligne) ──► [DATA] calcul ──► FAITS ──► base ──► [DEV] application
```
 
- **DEV produit les séries** (via l'API, jamais depuis le navigateur) et affiche les résultats.
- **DATA produit les faits** : les indicateurs calculés (jours de gel, GDD…), stockés dans `fact_indicateur`.
- Ce contrat fixe ce qui passe de l'un à l'autre : **le format de la série** (DEV → DATA) et **les deux fonctions d'échange**.
## 2. DEV → DATA : la série climatique
 
Une série = **une commune × un modèle**, **un jour par ligne**, avec ces 6 champs :
 
| Champ | Type | Unité / format | Règle |
|---|---|---|---|
| `id_commune` | entier | clé de `dim_commune` | obligatoire |
| `date` | texte | `YYYY-MM-DD` | obligatoire, une seule ligne par jour et par commune |
| `t_min` | décimal | °C | `temperature_2m_min` ; vide (`null`) si absent |
| `t_max` | décimal | °C | `temperature_2m_max` ; toujours ≥ `t_min` |
| `t_moy` | décimal | °C | `temperature_2m_mean` (si absent, DATA calcule (t_min+t_max)/2) |
| `precip` | décimal | mm | `precipitation_sum` ; vide traité comme 0 |
 
Exemple (une ligne) : `1,2000-07-01,8.6,19.1,14.5,0.09` (Lille, 1er juillet 2000).
 
**Ce que DEV livre :**
- une fonction **`recuperer_serie(id_commune, latitude, longitude, modele, date_debut, date_fin)`** qui renvoie la **liste de dictionnaires** `{id_commune, date, t_min, t_max, t_moy, precip}` (le modèle vient de `dim_modele.code_api`, jamais écrit en dur) ;
- les erreurs claires (API en erreur, réponse vide, timeout) : DEV les signale, DATA n'a pas à les deviner ;
- le **cache** et les nouvelles tentatives en cas de limite de débit (quota gratuit : 10 000 appels par jour et par adresse IP).
**Fichiers d'exemple pour tester sans l'API :**
- `Dossier Partie DEV/series-reel-MRI_AGCM3_2_S.csv` : échantillon **réel** (Lille et Reims, modèle MRI_AGCM3_2_S, 01/07/2000-31/12/2003 et 01/07/2040-31/12/2043), produit par `exporter_échantillons(DEV).py` ;
- `Dossier Partie DATA/series_test.csv` : jeu **synthétique** dont les résultats sont connus d'avance.
## 3. DATA → DEV : le module de calcul et les faits
 
**Calculer et enregistrer un fait :**
```python
from indicateurs import ligne_fait, sql_insert
ligne = ligne_fait(id_commune, id_culture, id_temps, id_modele,
                   serie, culture, latitude, annee_debut, annee_fin, id_session="global")
sql, params = sql_insert(ligne)       # INSERT paramétré (anti-injection)
cursor.execute(sql, params)
```
- `serie` : la liste de la section 2 ; `culture` : la ligne de `dim_culture` (dictionnaire) ; `latitude` : celle de `dim_commune`.
- `annee_debut` / `annee_fin` : les bornes de la période de `dim_temps`. DEV passe la série entière, DATA filtre les années.
**Lire les faits (pour l'affichage) :**
```sql
SELECT c.nom_commune, k.nom AS culture, t.libelle AS horizon, m.code_api AS modele,
       f.gdd_saison_cj, f.maturite_atteinte_pct, f.jours_gel, f.jours_stress_thermique,
       f.jours_t_optimale, f.pluie_saison_mm, f.bilan_hydrique_mm, f.nb_annees_calculees
FROM fact_indicateur f
JOIN dim_commune c ON c.id_commune = f.id_commune
JOIN dim_culture k ON k.id_culture = f.id_culture
JOIN dim_temps   t ON t.id_temps   = f.id_temps
JOIN dim_modele  m ON m.id_modele  = f.id_modele
WHERE f.id_commune = %s AND f.id_culture = %s AND f.id_session IN ('global', %s)
ORDER BY t.annee_debut, m.code_api;
```
Les paramètres sont toujours passés séparément, jamais collés dans le texte SQL. Pour l'affichage : comparer `1991-2020` et `2021-2050` pour montrer l'**évolution**, avec une réserve sur la valeur brute (les modèles peuvent sous-estimer le gel) et, dès qu'on a 2 modèles, la **fourchette** entre eux.
 
## 4. Règles communes
 
- **Jour de gel :** `t_min < seuil_gel_c` (strict). Une journée exactement au seuil n'est pas un gel (voir `Décisions_data.md`).
- **Valeur manquante :** un jour sans `t_min` ou sans `t_max` est ignoré ; une pluie manquante compte pour 0.
- **Incohérence :** un jour avec `t_min > t_max` déclenche une erreur côté DATA (DEV doit corriger la série).
- **ET0 :** elle n'est pas dans la série. DATA l'estime par Hargreaves. Le champ `et0_fao_evapotranspiration` de l'API renvoie `null` ; `et0_fao_evapotranspiration_sum` donne des millimètres, mais ses valeurs paraissent plus élevées : on ne l'utilise pas tant qu'elles ne sont pas contrôlées.
- **Projection ≠ prévision :** les chiffres sont des projections de modèles, donc incertains. L'application les présente avec nuance.
## 5. Choix retenus ensemble
 
| Sujet | Choix | Pourquoi |
|---|---|---|
| **Modèles** | `MRI_AGCM3_2_S` (repère) et `CMCC_CM2_VHR4` ; `MPI_ESM1_2_XR` en option | 2 familles différentes (atmosphère seule / couplé) ; l'énoncé demande au moins 2 modèles. `EC_Earth3P_HR` reste écarté (`actif = FALSE`) tant qu'on n'a pas revérifié ses données. |
| **Alimentation** | Pré-calcul de la grille (16 communes × 10 cultures × 2 horizons × modèles retenus), `id_session = 'global'` | L'application lit seulement la base : pas d'appel à l'API à l'affichage, donc pas de problème de quota. Le calcul à la demande viendra plus tard. |
| **Identité** | `id_session` anonyme fourni par DEV ; pas de comptes pour cette version | Conforme au backlog et à la conception RGPD ; `id_session` sert à isoler et à effacer les données d'un visiteur. |

## 6. Test de conformité (à refaire à chaque changement de format)

[x] DATA : `python test_indicateurs.py` réussit (16 tests), et le calcul des jours de gel tourne sur `series-reel-MRI_AGCM3_2_S.csv` sans modifier le fichier (requête en étoile et calcul_gel.py, vérifiés le [21/11/2026]).