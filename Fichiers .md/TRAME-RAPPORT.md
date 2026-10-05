# 📄 Trame du rapport final — Équipe 5 AgriFuture

> **SAÉ 3.01 « Climat & Cultures »** — structure attendue du rapport. Adaptez les longueurs, mais **couvrez toutes les sections**.
> 💡 Indications de pôle : 💻 = plutôt DEV · 📊 = plutôt DATA · 👥 = commun.

## Page de garde
Titre du projet · nom de l'équipe · membres (et parcours) · commanditaire (scénario) · date · année.

## Sommaire

## 1. Contexte & besoin 👥
- Présentation du scénario (Climat & Cultures) et du commanditaire.
- **Reformulation du besoin** (initialement flou) et périmètre retenu (cultures & communes).
- Utilisateurs visés (personas).

## 2. Analyse 👥
- Fonctionnalités priorisées (backlog) et **critères de faisabilité**.
- Choix structurants et contraintes (architecture dimensions / table de faits, séries via API, AlwaysData…).

## 3. Conception
- **3.1 Architecture applicative** 💻 : schéma, technos, **client de l'API Open-Meteo** (endpoints, gestion d'erreurs, cache), maquettes IHM.
- **3.2 Modèle de données** 📊 : **schéma en étoile** (dimensions), choix de modélisation, **référentiel cultures/seuils** (sources des seuils agronomiques).
- **3.3 Contrat d'interface** 👥 : comment l'appli consomme les dimensions et les faits.

## 4. Réalisation 💻
- Fonctionnalités développées, organisation du code, bonnes pratiques, **accessibilité/ergonomie**.

## 5. Exploitation des données 📊
- Requêtes et **calcul des indicateurs agro-climatiques** (GDD, gel, stress hydrique, décalage des zones…).
- **Restitution / visualisation** (cartes, courbes) et choix de présentation.

## 6. Sécurité & RGPD 📊💻
- Données personnelles traitées, mesures de protection, anonymisation/consentement.

## 7. Déploiement 👥
- Mise en production sur **AlwaysData** : procédure, configuration, difficultés rencontrées.

## 8. Tests & jeux d'essais 👥
- Stratégie de test, jeux d'essais (application **et** données), résultats.

## 9. Gestion de projet 👥
- Organisation (rôles, pôles), planning réel vs prévu (jalons J0→J5), **revues de sprint**, outils.
- Bilan de la **collaboration DEV ↔ DATA**.

## 10. 🤖 Volet « usage raisonné de l'IA » 👥
- Synthèse du **journal d'usage** (usages marquants, ce qui a été gardé/modifié/rejeté).
- 🌱 **Synthèse environnementale** : empreinte estimée (énergie, CO₂e), équivalences, **discussion de l'incertitude**, regard **coût/bénéfice**.
- Recul critique : limites de l'IA rencontrées, comment vous les avez gérées.

## 11. Conclusion 👥
- Bilan, **limites** du projet, **perspectives** d'amélioration.

## Annexes
- Journal d'usage de l'IA complet · charte signée · guide d'utilisation · captures · scripts BDD · …
