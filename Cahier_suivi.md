# Cahier de suivi — Équipe 5

SAÉ 3.01 « Climat & Cultures »

## Semaine 39 — Exploration & découverte

**Fait :**
- Exploration détaillée de l'API Open-Meteo Climate sur la commune de Lille (50,60 / 3,10) :
  - Test 1 : premier appel réussi (température max/min, précipitations) sur 1950-2050
  - Test 2 : élargissement à toutes les variables disponibles → ET0 non fournie par l'API
  - Test 3 : comparaison de deux modèles climatiques (MRI_AGCM3_2_S vs EC_Earth3P_HR) sur
    2023 → écarts significatifs (jusqu'à 30 jours de gel d'écart, 17 jours de forte chaleur
    d'écart)
  - Test 4 : comparaison Lille vs Briançon (même modèle) → contraste net (145 jours de gel à
    Briançon contre 6 à Lille)
- Lecture du glossaire et du document sur les modèles climatiques

**Bloquants rencontrés :**
- Limite de requêtes API horaires atteinte pendant le Test 3 → résolu en attendant la
  réinitialisation

**Décisions / constats pour la suite :**
- Le choix du modèle climatique et celui de la commune changent significativement les
  indicateurs → confirme la nécessité d'une approche multi-modèles et d'un traitement par
  commune
- L'ET0 devra être calculée manuellement (méthode Hargreaves)
- Le rate limit de l'API doit être anticipé côté DEV (système de cache)

## Semaine 40 — Rendu J1

**Fait :**
- Référentiel des 10 cultures sourcé et complété (chaque seuil agronomique a une source citée)
- Sources croisées via FAO ECOCROP, Arvalis, INRAE, IFV, IVES selon les cultures
- Document d'analyse finalisé : besoin reformulé, personas, backlog priorisé, critères de
  faisabilité, dimensions identifiées

**Points de vigilance identifiés :**
- Certaines valeurs du référentiel initial (GDD colza, GDD vigne) ne sont pas confirmées
  telles quelles par les sources trouvées — recoupement nécessaire, conforme à
  l'avertissement de l'énoncé qu'il n'existe pas de base officielle unique

**À faire :**
- Journal IA annexé (usages de l'IA déclarés et justifiés)
- Tag Git `jalon-1`
- Coordination finale avec le pôle DEV (maquettes IHM, test API client, architecture)
