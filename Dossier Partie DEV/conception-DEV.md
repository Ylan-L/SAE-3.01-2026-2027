# Document de conception — Pôle DEV — Équipe 5 « AgriFutur »

SAÉ 3.01 « Climat & Cultures » · Jalon 2 · version 2 · pôle DEV, équipe 5
Complète le **CONTRAT-INTERFACE.md** (DEV ↔ DATA) : ce document dit comment DEV le met en œuvre.

## 1. L'application en bref

Un utilisateur choisit une **commune**, une **culture**, un **horizon** et lit un **verdict** : l'évolution entre 1991-2020 et 2021-2050, avec la fourchette entre modèles. Les chiffres ne sont pas calculés pendant la visite : ils sont **pré-calculés puis lus en base**.

```
 ┌─ Préparation (script DEV, une fois) ─────────────────────────────────────────────┐
 │ Open-Meteo ──► client API (+ cache disque) ──► indicateurs.py (DATA) ──► MariaDB │
 └──────────────────────────────────────────────────────────────────────────────────┘
 ┌─ Visite ───────────────────────────────────────────────────────────────────────┐
 │ Navigateur ◄──pages HTML── Flask ◄──SELECT── MariaDB (fact_indicateur + dim_*) │
 └────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Choix techniques

| Choix | Décision | Pourquoi (critère déterminant) | Risque |
|---|---|---|---|
| Back-end | **Flask (Python)** | Le module de calcul DATA et le client API du kit sont en Python : on les importe tels quels, un seul langage à défendre | Déploiement Flask sur AlwaysData à tester |
| Base | **MariaDB** (choix DATA, `bddsae_agri`) | Partagée entre pôles, schéma en étoile déjà écrit | — |
| Front | **Pages rendues par Flask (Jinja) + un peu de JS pour les graphiques** | Les pages HTML/CSS de la maquette deviennent des gabarits ; peu de JS à écrire | Rechargement à chaque choix (acceptable) |
| Alimentation | **Pré-calcul de toute la grille** | L'appli ne dépend plus de l'API en visite : pas de quota ni de timeout côté utilisateur | Quota au moment du pré-calcul (§3) |
| Comptes | **Aucun au MVP** | « Souhaitable » dans la maquette, absent du Must du backlog ; aucune donnée personnelle à gérer | Reporté en version 2 |
| Cache | **Disque (client du kit)** | Déjà écrit ; chaque réponse API n'est demandée qu'une fois | Local au serveur, sans expiration |

## 3. Préparation des données (client API)

**Grille** : 16 communes × 10 cultures × 2 horizons × 2 modèles = 640 lignes de `fact_indicateur`. Les cultures partagent la même série : il suffit de **32 séries** (commune × modèle).

**Une série** (contrat §1) : `id_commune, date, t_min, t_max, t_moy, precip`, un jour par ligne, de 1991 à 2050 (« DEV passe la série entière, DATA filtre »). Le client la demande en **2 tranches de 30 ans** (= les 2 horizons de `dim_temps`), chacune mise en cache. Les 4 variables sont dans un seul appel ; `disable_bias_correction` n'est jamais envoyé ; le modèle vient de `dim_modele.code_api`.

**Quota** : environ 1 600 appels pondérés par série, soit ~50 000 pour la grille, au-delà des 10 000 par jour et par IP de l'API gratuite. Il faut donc la **clé Moodle** (serveurs sans limite par IP) ou étaler sur plusieurs jours : le cache permet de reprendre où l'on s'était arrêté.

**Erreurs** (alignées sur le contrat §1) :

| Cas | Réaction |
|---|---|
| 429 (quota) | 4 tentatives espacées (kit), puis arrêt propre ; la reprise repart du cache |
| API injoignable | arrêt de la série concernée, journalisé |
| Modèle qui renvoie du vide (réponse vide, variable absente) | `RuntimeError` → on signale le modèle (`dim_modele.actif = FALSE`) |
| `t_min > t_max` | comptés (`jours_incoherents`) et signalés à DATA, qui lève l'erreur |
| Valeur manquante | laissée à `None` ; DATA ignore le jour (`precip` manquante = 0) |
| Paramètres invalides | refusés avant tout appel réseau |

## 4. Contrat d'interface : ce que DEV applique

| Point du contrat | Mise en œuvre DEV |
|---|---|
| §1 série DEV → DATA | `series_contrat.recuperer_series(...)` (11 + 2 tests hors ligne) |
| §2 module de calcul | `ligne_fait(...)` puis `sql_insert(...)` ; `annee_debut/annee_fin` = bornes de `dim_temps` ; `id_session = "global"` |
| §3 lecture des faits | la requête du contrat, exécutée avec des paramètres séparés ; jamais de SQL concaténé |
| ET0 | non fournie par l'API : estimée par DATA (Hargreaves) |

**Points « À valider ensemble » du contrat : proposition DEV**
- **Modèles** : `MRI_AGCM3_2_S` (recommandé par l'énoncé, le plus riche en variables) et `CMCC_CM2_VHR4` (institution européenne différente, résolution proche : 30 km contre 20 km, ce qui rend l'écart entre modèles attribuable au modèle plutôt qu'à la maille). DEV vérifie qu'ils renvoient des données avant usage (T3) ; DATA juge leur plausibilité.
- **Alimentation** : pré-calcul de toute la grille (section 2). C'est le choix DEV parmi les deux options laissées ouvertes par le contrat.
- **`id_session`** : valeur `"global"` au MVP (pas de comptes) ; la question de l'identité se repose en version 2.

## 5. Pages du MVP

| Page (maquette) | Données | Source |
|---|---|---|
| Accueil | texte | — |
| Choisir | listes communes, cultures, horizons, modèles | `dim_*` |
| Résultat | indicateurs d'une commune × culture, 2 horizons, tous modèles | requête du contrat §3 |
| Évolution du climat | comparaison 1991-2020 → 2021-2050 par indicateur | mêmes faits |
| Erreur / attente | message selon le cas | — |

Routes : `/`, `/explorer`, `/resultat?commune=&culture=`, `/evolution?commune=`, `/methodologie`. Entrées validées (listes blanches). Les pages de la maquette sont dans `site/projet_1/` (branche `dev-thenujan`) et servent de gabarits.

**Règles d'affichage** (contrat §3 et fiche maquette) : montrer d'abord l'**évolution** entre les deux horizons, puis une réserve sur la valeur brute (les modèles sous-estiment le gel) ; « projection » et jamais « prévision » ; fourchette entre modèles ; source des seuils visible ; jamais la couleur seule ; responsive.
La courbe année par année est « Souhaitable » : elle demande les séries, hors du pré-calcul.

## 6. Sécurité et RGPD

- Clé API et identifiants MariaDB dans `.env`, exclu de Git.
- Requêtes SQL toujours paramétrées ; entrées validées côté serveur.
- **Aucune donnée personnelle collectée au MVP** (pas de comptes) ; seuls subsistent les journaux techniques d'AlwaysData. La conception RGPD détaillée relève de DATA.

## 7. Plan de tests

| N° | Cas | Entrée → attendu | Auto/manuel | Statut |
|---|---|---|---|---|
| T1 | Format du contrat | réponse simulée → 6 colonnes dans l'ordre, valeurs manquantes comptées | auto | fait |
| T2 | Série entière | 1991-2050 → 2 appels (1991-2020, 2021-2050), lignes concaténées sans doublon | auto | fait |
| T3 | Réponses inexploitables | vide, variable vide, longueurs incohérentes → `RuntimeError` | auto | fait |
| T4 | Paramètres invalides | latitude, date, bornes, période > 61 ans, modèle vide → refus sans appel réseau | auto | fait |
| T5 | `t_min > t_max` | → compté dans `jours_incoherents` | auto | fait |
| T6 | Calcul des indicateurs | `series_test.csv` → valeurs attendues de DATA | auto (`test_indicateurs.py`) | fait (DATA) |
| T7 | Cache | même requête 2 fois → 1 seul appel API | manuel | à faire |
| T8 | Quota 429 | API simulée → tentatives puis arrêt propre | auto | à faire |
| T9 | Échantillon réel | 1 commune, 1 an → fichier au contrat, taux de manquants noté | manuel | à faire |
| T10 | Route `/resultat` | commune inconnue → erreur 400 | auto | à faire |
| T11 | Parcours IHM | Accueil → Choisir → Résultat avec mention « projection » | manuel | à faire |
| T12 | Déploiement | URL AlwaysData : accueil + un résultat | manuel | à faire |

## 8. Risques principaux

| Risque | Mesure |
|---|---|
| Quota (≈ 50 000 appels pour la grille) | clé Moodle, cache, pré-calcul reprenable |
| Flask sur AlwaysData non testé | déploiement de test avant la fin du J2 |
| Modèle sans données | contrôle avant usage (T3), `actif = FALSE` |
| Fenêtres de saison de plusieurs cultures non sourcées (hypothèses d'équipe) | validation par DATA en J2.4, fiabilité affichée |
| Pages de la maquette sur la branche `dev-thenujan`, pas encore dans `main` | fusion avant l'intégration |
