# Document d'analyse — Équipe 5

SAÉ 3.01 « Climat & Cultures » — Jalon 1

## 1. Reformulation du besoin

Le commanditaire souhaite un outil qui aide les acteurs agricoles à anticiper l'évolution du
climat sur leur territoire à horizon 2050. Notre application croise les projections climatiques
de l'Open-Meteo Climate API avec des seuils agronomiques propres à chaque culture, pour
indiquer si une culture restera viable dans une commune donnée.

Le périmètre retenu couvre 10 cultures (blé tendre, orge, colza, maïs, tournesol, soja,
betterave sucrière, pomme de terre, vigne, olivier) et 16 communes représentatives des
climats français, avec une projection à horizon 2050.

## 2. Personas / utilisateurs

### Persona 1 — Marc, agriculteur céréalier
- **Âge / situation** : 45 ans, exploite 80 hectares dans la Somme
- **Objectif** : savoir si sa culture actuelle restera viable d'ici 2050
- **Niveau technique** : aucune connaissance en climatologie, pas informaticien
- **Attente** : une réponse claire et actionnable, sans jargon technique affiché

### Persona 2 — Léa, conseillère agricole en chambre d'agriculture
- **Âge / situation** : 32 ans, accompagne plusieurs exploitants de son secteur
- **Objectif** : comparer plusieurs cultures et communes pour conseiller ses clients
- **Niveau technique** : à l'aise avec les chiffres, veut comprendre l'incertitude entre modèles
- **Attente** : une vue plus détaillée, accès aux sources et aux écarts entre modèles

## 3. Backlog priorisé (MoSCoW)

###  Must have — Indispensable
| Fonctionnalité | Pourquoi |
|---|---|
| Sélectionner une culture (parmi les 10 sourcées) et une commune (parmi les 16) | Cœur du parcours utilisateur |
| Récupérer les données climatiques via l'API Open-Meteo pour cette culture/commune | Sans données, pas d'indicateur |
| Calculer au moins un indicateur agro-climatique (ex. jours de gel) en croisant données + seuils du référentiel | Valeur ajoutée du projet |
| Afficher le résultat de façon lisible (graphique ou chiffre clair) | Le persona Marc doit comprendre sans jargon |
| Utiliser au moins un modèle climatique avec sa source citée | Base minimale de la restitution |
| Gérer les erreurs de l'API (rate limit, données manquantes) | Rencontré concrètement pendant nos tests |
| Déploiement fonctionnel sur AlwaysData | Exigé dès J0 par l'énoncé |

###  Should have — Souhaitable
| Fonctionnalité | Pourquoi |
|---|---|
| Comparer plusieurs modèles climatiques pour la même culture/commune | Prouvé nécessaire par nos tests (écarts significatifs entre modèles) |
| Calculer un 2e indicateur (ex. GDD ou stress hydrique) | Enrichit l'appli |
| Comparer plusieurs communes entre elles | Utile pour le persona Léa |
| Visualisation graphique (évolution dans le temps jusqu'à 2050) | Meilleure lisibilité |
| Afficher la source et la fiabilité des seuils utilisés | Renforce la confiance utilisateur |
| Message d'incertitude visible entre modèles | Honnêteté scientifique |

###  Could have — Si le temps le permet
| Fonctionnalité | Pourquoi |
|---|---|
| Carte interactive de France avec les communes cliquables | Confort visuel |
| Export des résultats en PDF ou CSV | Confort, non bloquant |
| Comparaison simultanée de plusieurs cultures sur une commune | Croisement supplémentaire |
| Calcul de l'ET0 (méthode Hargreaves) | Améliore la précision, complexe à implémenter |
| Mode "analogue climatique" | Idée périphérique |

###  Won't have — Hors périmètre
| Fonctionnalité | Pourquoi exclu |
|---|---|
| Comptes utilisateurs / authentification | Pas demandé par le scénario |
| Interface d'administration (ajout communes/cultures) | Hors périmètre du commanditaire |
| Prévisions météo court terme | Hors sujet (projection ≠ prévision) |
| Application mobile native | Non demandé |
| Alertes/notifications automatiques | Hors cadre du projet académique |

## 4. Critères de faisabilité

- **Techniquement faisable** : l'API répond de façon fiable (tests 1-2), mais impose un rate
  limit horaire → nécessite un système de cache côté DEV.
- **Données incomplètes** : l'ET0 n'est pas fournie par l'API (à déterminer);
  certains seuils agronomiques (GDD colza, GDD olivier) ne sont pas confirmés
  par une source unique et fiable — recoupement nécessaire, cohérent avec l'avertissement de
  l'énoncé qu'il n'existe pas de base officielle unique.
- **Contrainte de temps** : 10 cultures × 16 communes × plusieurs modèles représentent trop
  de combinaisons pour un MVP → le périmètre de départ sera volontairement restreint.
- **Contrainte IA** : enveloppe de 15$ par équipe sur Claude Haiku 4.5, à utiliser avec
  sobriété pour la conserver jusqu'à la fin du projet.

## 5. Dimensions nécessaires et qualité des données

### Dimensions pressenties (schéma en étoile)
- `Dim_Culture` — le référentiel des 10 cultures sourcées
- `Dim_Commune` — les 16 communes (lat/lon, altitude, zone climatique)
- `Dim_Temps` — les dates journalières fournies par l'API
- `Dim_Modele` — les modèles climatiques (ex. MRI_AGCM3_2_S, EC_Earth3P_HR)
- `Fait_Indicateur` — table de faits croisant culture × commune × modèle × date

### Qualité / format des données observés
- Dates au format `iso8601`(AAAA-MM-DD-HH-MIN-SS), températures en `°C`, précipitations en `mm`
- ET0 non fournie par l'API (`undefined`)
- Résolution native ~10 km, un seul scénario d'émission
- Écarts significatifs constatés entre modèles climatiques et entre communes
- Rate limit horaire de l'API à anticiper techniquement
