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
| Thenujan NANTHAKUMAR | [à compléter ou « Aucun »] | | |
| Samuel MIHAILA | [à compléter ou « Aucun »] | | |
| Ylan LEANG | [à compléter ou « Aucun »] | | |
| Adam MURDAKHAIEV | Haiku 4.5  | VS Code| 05/10/2026 |
| Nabil MERZOUK | [à compléter ou « Aucun »] | | |

*Aucun assistant ambiant utilisé ? Écrivez-le explicitement : « Aucun » — une case vide n'est pas une déclaration.*

---

## Journal

| Date | Équipier | Outil/modèle | Tâche / contexte | Prompt (résumé) | Sortie IA | Gardé/modifié/rejeté | Justification (vérif. / correction / test) | Tokens (≈) |
|05/10/2026|Adam|Haiku 4.5 | Test de la clé A et du script d'empreinte Explique en 3 phrases ce qu'est une base de données relationnelle » (question par défaut du script) | Définition d'une BDD relationnelle | **rejeté** (juste un test, pas intégré au projet) | Vérifié que la clé est bien vue et que le comptage de tokens s'affiche | 172 |

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
