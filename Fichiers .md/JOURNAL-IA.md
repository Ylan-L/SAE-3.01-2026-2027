# 📓 Journal d'usage de l'IA — Équipe `5`

> **SAÉ 3.01 « Climat & Cultures »** — à tenir **au fil de l'eau**, versionné dans le dépôt Git, annexé au livrable final.
> Membres : Adrien GARRIGON-VIRAMOUTOU, Thenujan NANTHAKUMAR, Samuel MIHAILA, Ylan LEANG, Adam MURDAKHAIEV, Nabil MERZOUK

## Rappel express des règles
- L'IA est un **copilote, pas un sous-traitant**. 🔑 *« Si tu ne peux pas l'expliquer, tu ne peux pas le rendre. »*
- **Tout outil est autorisé** (Claude fourni, ChatGPT, Gemini, Copilot…) — **à condition d'être déclaré**.
- **Une ligne par usage significatif** (code/requête/texte intégré, debug qui change la solution, choix orienté, tests, refactor).
- **Nominatif** : chaque ligne identifie son auteur.
- **Jamais** de données personnelles dans les prompts.
- La colonne **Justification** est le cœur : *pourquoi* + ce que vous avez **vérifié / corrigé / testé**.

---

## ⌨️ Déclaration permanente — assistants ambiants

> **À remplir en J0, une fois pour toutes.** Un assistant d'autocomplétion (Copilot, Tabnine, IA intégrée à l'IDE…) produit des suggestions **en continu** : impossible de les journaliser une par une. On le déclare donc **globalement** ici.
> ⚠️ La règle d'or continue de s'appliquer : ce que vous intégrez, vous devez savoir l'expliquer.

| Équipier | Outil ambiant utilisé | Où (IDE / éditeur) | Depuis quand |
|---|---|---|---|
| Adrien GARRIGON-VIRAMOUTOU | [à compléter ou « Aucun »] | | |
| Thenujan NANTHAKUMAR | Haiku 4.5 | VS Code| 17/10/2026 |
| Samuel MIHAILA | [à compléter ou « Aucun »] | | |
| Ylan LEANG | GitHub Copilot | VS Code | Fin 2025 |
| Adam MURDAKHAIEV | Haiku 4.5  | VS Code| 05/10/2026 |
| Nabil MERZOUK | [à compléter ou « Aucun »] | | |

*Aucun assistant ambiant utilisé ? Écrivez-le explicitement : « Aucun » — une case vide n'est pas une déclaration.*

---

## Journal

| Date | Équipier | Outil/modèle | Tâche / contexte | Prompt (résumé) | Sortie IA | Gardé/modifié/rejeté | Justification (vérif. / correction / test) | Tokens (≈) |
|---|---|---|---|---|---|---|---|---|
| 05/10/2026 | Adam | Haiku 4.5 | Test de la clé A et du script d'empreinte Explique en 3 phrases ce qu'est une base de données relationnelle | (question par défaut du script) | Définition d'une BDD relationnelle | **rejeté** (juste un test, pas intégré au projet) | Vérifié que la clé est bien vue et que le comptage de tokens s'affiche | 172 |
| 12/10/2026 | Adam | Haiku 4.5 | Comprendre le schéma en étoile avant de modéliser la BDD (SAÉ) | « Explique en quelques phrases ce qu'est un schéma en étoile, avec un exemple simple » | Définition (table de faits centrale + tables de dimensions) et exemple d'une boutique : faits = ventes ; dimensions = produit, temps, client, magasin ; schéma exemple | **gardé** (compris, non copié dans le livrable) | Comparé à quelque recherche que j'ai fait ; je vais relié cela à notre propre schéma (dim_commune, dim_culture, Fact_Indicateur) pour vérifier que j'ai compris le rôle de chaque table | 336 |
| 17/11/2026 | Adam | Haiku 4.5 (API, script poc-empreinte-ia.py) | Savoir écrire et lancer un SELECT dans phpMyAdmin pour la base bddsae_agri | « Explique-moi en quelques phrases comment faire un SELECT sur phpMyAdmin » | Deux méthodes (interface graphique « Parcourir », onglet SQL) avec des exemples génériques (`ma_table`, `utilisateurs`) | **gardé** (compris, exemples non copiés tels quels) | [À CONFIRMER avant rendu : testé un SELECT dans l'onglet SQL sur bddsae_agri (ex. `SELECT * FROM dim_commune`) ; exemples génériques adaptés à nos tables.] | 317 (entrée 26 / sortie 291) |
| 17/10/2026 | Thenujan NANTHAKUMAR | claude-haiku-4-5 | Préparation des tests de test_indicateurs.py | Propose 5 cas limites pour tester une fonction qui compte les jours de canicule. | Proposition de 5 cas limites avec des exemples de tests Python | **Gardé** | Les cas proposés constituent des pistes pour compléter les tests de la fonction. Leur pertinence doit être vérifiée par rapport à son fonctionnement réel. | ~330 (entrée 30 / sortie 300) |
| 24/11/2026 | Thenujan NANTHAKUMAR | claude-haiku-4-5 | Comprendre le lien entre les pôles DATA et DEV pour travailler sur app.py | Comment relier le fonctionnement entre la partie DATA et la partie DEV en Python ? | Présentation de plusieurs approches pour connecter les traitements DATA et DEV | **Modifié** | Les explications ont servi de base de compréhension. Les solutions doivent être adaptées aux modules et aux contrats d'interface réellement utilisés dans le projet. | ~327 (entrée 27 / sortie 300) |
| 24/11/2026 | Thenujan NANTHAKUMAR | claude-haiku-4-5 | Comprendre le fonctionnement d'une API REST | Peux-tu expliquer simplement le fonctionnement d'une API REST ? | Explication du rôle d'une API REST et des échanges entre applications | **Gardé** | Explication utilisée pour comprendre le principe des échanges avec un service externe. Aucun code directement repris dans le projet. | ~328 (entrée 28 / sortie 300) |
| 24/11/2026 | Thenujan NANTHAKUMAR | claude-haiku-4-5 | Comprendre la gestion des erreurs lors d'un appel API | Comment gérer proprement les erreurs lors d'un appel API en Python ? | Présentation de la gestion des erreurs avec try-except et des bonnes pratiques | **Modifié** | Les principes proposés sont utiles, mais les exemples doivent être adaptés à notre client Open-Meteo qui utilise urllib. | ~325 (entrée 25 / sortie 300) |
| 24/11/2026 | Thenujan NANTHAKUMAR | claude-haiku-4-5 | Préparer les tests d'une fonction de récupération de données météorologiques | Quels tests simples peut-on réaliser sur une fonction qui récupère des données météorologiques ? | Proposition de tests de réussite et de cas d'erreur pour une fonction météo | **Modifié** | Les propositions servent de pistes pour préparer les tests. Elles doivent être adaptées aux fonctions réellement présentes et exécutées pour confirmer leur validité. | ~333 (entrée 33 / sortie 300) |
| 25/11/2026 | Ylan LEANG | Claude-haiku-4-5 | Test de la clé API | Définition d'un GDD | Définition d'un GDD	| **rejeté** (juste un test, pas intégré au projet) | Vérifier que l'appel fonctionne et que le comptage de tokens s'affiche | 117 |
*(Ajoutez autant de lignes que nécessaire — notamment celles des autres membres de l'équipe.)*

---

## 🌱 Synthèse environnementale (à compléter pour le rendu final)

> Méthode et exemple de calcul : voir `poc-empreinte-ia.py`. Manier avec **esprit critique** (forte incertitude).

- **Total tokens** sur le projet : `[…]` (entrée : `[…]` / sortie : `[…]`)
- **Énergie estimée** : `[…]` Wh
- **CO₂e estimé** : `[…]` g
- **Équivalence parlante** : ≈ `[…]` (ex. m/km en voiture, via facteur ADEME)
- **Hypothèses retenues** : `[Wh/1k tokens, intensité carbone du réseau, modèle…]`
- **Périmètre de la mesure** : `[quels usages ai-je pu compter, lesquels non ?]`
  > ℹ️ La colonne **Tokens** n'est renseignable que pour le compte API fourni. Un usage sur ChatGPT, Gemini ou Copilot n'expose pas ses tokens : **écrivez « non mesurable »** dans la colonne et dites-le ici. Annoncer ce qu'on n'a **pas** pu mesurer fait partie d'une mesure honnête — c'est valorisé, pas pénalisé.
- **Discussion de l'incertitude** : `[pourquoi ces chiffres varient d'un facteur ~10 ?]`
- **Regard coût/bénéfice** : `[cet usage de l'IA en valait-il la peine ? où aurait-on pu être plus sobre ?]`
