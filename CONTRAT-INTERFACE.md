# Contrat d'interface DEV ↔ DATA — projet « Climat & Cultures »

> Brouillon proposé par le pôle DATA à valider avec le pôle DEV (livrable commun J2).

## 1. DEV → DATA : la série climatique (1 jour = 1 ligne)

| Champ | Type | Unité / format | Règle |
|---|---|---|---|
| `id_commune` | entier | clé de `dim_commune` | obligatoire |
| `date` | texte | `YYYY-MM-DD` | obligatoire, une seule ligne par jour et par commune |
| `t_min` | décimal | °C | `temperature_2m_min` ; `null` si absent |
| `t_max` | décimal | °C | `temperature_2m_max` ; toujours ≥ `t_min` |
| `t_moy` | décimal | °C | `temperature_2m_mean` (sinon DATA recalcule (t_min+t_max)/2) |
| `precip` | décimal | mm | `precipitation_sum` ; `null` traité comme 0 |

- Une série = **une commune × un modèle**. Le modèle est fourni **à part** (paramètre `id_modele`, lu dans `dim_modele`, jamais écrit en dur).
- Échange : liste de dictionnaires Python (ou CSV UTF-8, séparateur virgule, mêmes noms de colonnes). Exemple : `DATA/series_test.csv`.
- **ET0 n'est pas dans la série** : l'API Climate la renvoie à `null` ; DATA l'estime par Hargreaves.
- Erreurs : jour avec `t_min > t_max` → DATA lève une erreur ; valeur manquante → le jour est ignoré. DEV signale en amont tout modèle qui renvoie des données vides (`dim_modele.actif = FALSE`).

## 2. DATA → DEV : le module de calcul
```python
from indicateurs import ligne_fait, sql_insert
ligne = ligne_fait(id_commune, id_culture, id_temps, id_modele,
                   serie, culture, latitude, annee_debut, annee_fin, id_session="global")
sql, params = sql_insert(ligne)       # INSERT ... ON DUPLICATE KEY UPDATE, paramétré
cursor.execute(sql, params)
```
- `culture` = la ligne de `dim_culture` sous forme de dict ; `latitude` = `dim_commune.latitude`.
- `annee_debut/annee_fin` = les bornes de `dim_temps` (1991-2020 ou 2021-2050) : DEV passe la série entière, DATA filtre.

## 3. DATA → DEV : lire les faits
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
Paramètres toujours passés séparément (jamais concaténés). Comparer `1991-2020` et `2021-2050` pour afficher d'abord l'**évolution**, puis une réserve sur la valeur brute (les modèles sous-estiment le gel).

## 4. À valider ensemble
- [ ] Liste finale des modèles (≥ 2) — décision à deux (DEV filtre technique, DATA plausibilité).
- [ ] Mode d'alimentation : pré-calcul de toute la grille **ou** à la demande.
- [ ] Gestion de `id_session` / `id_utilisateur` (qui fournit l'identité).
