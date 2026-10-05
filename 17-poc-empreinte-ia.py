# -*- coding: utf-8 -*-
"""
🌱 Mesurer l'empreinte de votre usage de l'IA — SAÉ 3.01 « Climat & Cultures »
==============================================================================

POURQUOI CE SCRIPT
    Votre rendu final comporte une « synthèse environnementale » de votre usage de
    l'IA (voir votre JOURNAL-IA.md). Pour la calculer, il faut deux choses :
      1. savoir COMPTER ce que consomme un appel à l'IA : des TOKENS ;
      2. savoir CONVERTIR ces tokens en énergie (Wh) et en CO₂.
    Ce script vous montre les deux, sur un exemple, puis fait le calcul pour votre
    bilan de fin de projet.

LES DEUX FAÇONS DE L'UTILISER
    python 17-poc-empreinte-ia.py
        → envoie UNE question à Claude, affiche les tokens consommés et
          l'empreinte de cet appel. (Vous pouvez poser votre propre question :
          python 17-poc-empreinte-ia.py "Explique-moi une jointure SQL")

    python 17-poc-empreinte-ia.py --bilan 250000
        → n'appelle PAS l'IA. Calcule l'empreinte d'un total de tokens :
          celui que vous avez additionné dans votre journal en fin de projet.

AVANT DE COMMENCER — installer les bibliothèques
    pip install anthropic ecologits python-dotenv
    (ecologits est facultatif : sans lui, seul le calcul « à la main » est fait.)

OÙ METTRE LA CLÉ — deux façons, au choix
    Votre enseignant vous a remis une clé qui commence par « sk-ant-api03- ».
    ⚠️ Elle ne s'écrit JAMAIS dans ce fichier, ni dans aucun fichier de code : un
    fichier de code finit dans Git, et une clé publiée sur Git est une clé volée.

    ▶ FAÇON 1 — un fichier .env  (recommandée en équipe)
      1. Dans le MÊME dossier que ce script, créez un fichier nommé exactement
         .env   (un point, puis « env », sans rien d'autre : pas de .txt à la fin).
      2. Écrivez-y une seule ligne, sans espaces ni guillemets :
             ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx
      3. Ouvrez le fichier .gitignore du projet et vérifiez qu'il contient la ligne :
             .env
         (le .gitignore du kit de démarrage la contient déjà). Sans elle, votre
         clé partirait dans Git au prochain commit.
      Le script lit ce fichier tout seul, grâce à python-dotenv.

    ▶ FAÇON 2 — une variable d'environnement  (une fois pour toutes, sur votre poste)
      • Windows, dans un terminal :
             setx ANTHROPIC_API_KEY "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx"
        puis FERMEZ ET ROUVREZ VS Code : un simple nouveau terminal ne suffit pas,
        VS Code ne relit les variables qu'à son démarrage.
      • macOS / Linux : ajoutez à la fin de ~/.zshrc (ou ~/.bashrc) la ligne
             export ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx"
        puis ouvrez un nouveau terminal.

    Pour vérifier : lancez ce script. S'il affiche « Aucune clé trouvée », la clé
    n'est pas vue — relisez les étapes ci-dessus. Tout est aussi expliqué dans la
    fiche « Mise en route — clé API » (18-mise-en-route-cle-API.pdf).

À GARDER EN TÊTE
    Ces estimations sont très incertaines : selon les hypothèses, elles varient d'un
    facteur 10, voire davantage. Ce n'est pas un défaut du script, c'est la réalité
    du sujet. Comme pour les projections climatiques de votre application, on
    annonce une FOURCHETTE et ses hypothèses, pas un chiffre faussement précis.
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")    # accents et symboles dans le terminal Windows
except Exception:
    pass

# FAÇON 1 : si un fichier .env existe à côté de ce script (ou dans un dossier parent),
# on le charge. La clé devient alors une variable d'environnement, comme en FAÇON 2.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    load_dotenv()                       # puis les dossiers parents, en complément
except ImportError:
    pass                                # pas de python-dotenv : seule la FAÇON 2 marche

# C'est le SEUL modèle ouvert sur le compte de votre équipe (voir la charte d'usage
# de l'IA). Tout autre nom de modèle renverra une erreur.
MODELE = "claude-haiku-4-5"


# =========================================================================
# LES HYPOTHÈSES — c'est ici que tout se joue
# =========================================================================
# Personne ne publie la consommation exacte d'un appel à un modèle d'IA. On travaille
# donc avec des ORDRES DE GRANDEUR, en encadrant chaque valeur par une fourchette.
# Vous pouvez — et c'est même conseillé — les remplacer par des valeurs trouvées dans
# une source que vous citerez dans votre synthèse.
#
#                        (basse, centrale, haute)
WH_PAR_1000_TOKENS     = (0.1,   0.3,      0.6)
#   Énergie consommée par le serveur pour traiter 1 000 tokens, en Wh.
#   Dépend du modèle, du matériel, du taux de remplissage du centre de données…

G_CO2_PAR_KWH          = (50,    380,      480)
#   Intensité carbone de l'électricité, en grammes de CO₂e par kWh.
#   50 ≈ électricité française (très peu carbonée) · 380 ≈ centre de données
#   « moyen » · 480 ≈ moyenne mondiale. On ne sait pas où tourne le serveur :
#   d'où l'écart.

# Deux équivalences pour rendre les chiffres parlants — à vérifier vous-mêmes, par
# exemple sur le site Impact CO2 de l'ADEME : https://impactco2.fr
G_CO2_PAR_KM_VOITURE   = 120    # ordre de grandeur, voiture thermique récente
WH_PAR_CHARGE_TELEPHONE = 12    # ordre de grandeur, une charge complète de smartphone


# =========================================================================
# LE CALCUL (le même dans les deux modes)
# =========================================================================
def empreinte(tokens):
    """Renvoie (énergie en Wh, CO₂e en g) pour les hypothèses basses, centrales et hautes."""
    resultats = []
    for wh_1000, g_kwh in zip(WH_PAR_1000_TOKENS, G_CO2_PAR_KWH):
        wh = tokens / 1000 * wh_1000          # tokens → énergie
        g = wh / 1000 * g_kwh                  # énergie → CO₂e   (1 kWh = 1 000 Wh)
        resultats.append((wh, g))
    return resultats


def fr(x):
    """3 chiffres significatifs, virgule décimale : 28.5 → « 28,5 »."""
    return f"{x:.3g}".replace(".", ",")


def afficher_empreinte(tokens):
    (wh_b, g_b), (wh_c, g_c), (wh_h, g_h) = empreinte(tokens)
    print(f"\n--- Estimation « à la main » pour {tokens:,} tokens ---".replace(",", " "))
    print(f"  Énergie : {fr(wh_c)} Wh   (fourchette : {fr(wh_b)} à {fr(wh_h)} Wh)")
    print(f"  CO₂e    : {fr(g_c)} g    (fourchette : {fr(g_b)} à {fr(g_h)} g)")
    print("\n  Pour se représenter la valeur centrale :")
    print(f"  • {fr(wh_c / WH_PAR_CHARGE_TELEPHONE)} charge(s) de smartphone")
    print(f"  • {fr(g_c / G_CO2_PAR_KM_VOITURE * 1000)} mètre(s) en voiture thermique")
    print("\n  Hypothèses (à recopier dans votre synthèse) :")
    print(f"  • {fr(WH_PAR_1000_TOKENS[1])} Wh pour 1 000 tokens "
          f"(fourchette {fr(WH_PAR_1000_TOKENS[0])} à {fr(WH_PAR_1000_TOKENS[2])})")
    print(f"  • {G_CO2_PAR_KWH[1]} g CO₂e par kWh "
          f"(fourchette {G_CO2_PAR_KWH[0]} à {G_CO2_PAR_KWH[2]})")
    print("  Les bornes combinent les hypothèses les plus basses, puis les plus hautes :")
    print("  l'écart est large, et c'est normal. Écrivez-le plutôt que de le cacher.")


# =========================================================================
# MODE 1 — Un appel à Claude, et ce qu'il consomme
# =========================================================================
def demonstration(question):
    # Deux vérifications d'abord, pour un message clair plutôt qu'une erreur Python.
    try:
        import anthropic
    except ImportError:
        sys.exit("❌ La bibliothèque « anthropic » n'est pas installée.\n"
                 "   Tapez :  pip install anthropic ecologits\n"
                 "   (dans le terminal de VS Code, avec le bon environnement Python sélectionné)")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("❌ Aucune clé trouvée. Deux façons de la fournir (détails en tête de ce fichier) :\n"
                 "   1. un fichier .env, à côté de ce script, contenant la ligne\n"
                 "        ANTHROPIC_API_KEY=sk-ant-api03-...\n"
                 "      (et pip install python-dotenv) ;\n"
                 "   2. une variable d'environnement : setx ANTHROPIC_API_KEY \"sk-ant-api03-...\"\n"
                 "      puis fermez et rouvrez VS Code.\n"
                 "   (Le mode --bilan, lui, fonctionne sans clé.)")

    # EcoLogits doit être activé AVANT le premier appel : il « enveloppe » le client
    # Anthropic pour calculer l'impact de chaque réponse. S'il est absent, ou s'il
    # ne connaît pas le modèle, on se contente du calcul à la main.
    ecologits_actif = False
    try:
        from ecologits import EcoLogits
        EcoLogits.init(providers=["anthropic"], electricity_mix_zone="FRA")
        ecologits_actif = True
    except Exception as e:
        print(f"[info] EcoLogits indisponible ({type(e).__name__}) : calcul à la main seulement.")

    try:
        # Aucune clé dans le code : le client la lit dans la variable d'environnement
        # ANTHROPIC_API_KEY, remplie soit par votre fichier .env, soit par setx.
        client = anthropic.Anthropic()
        reponse = client.messages.create(
            model=MODELE,
            max_tokens=300,
            messages=[{"role": "user", "content": question}],
        )
    except anthropic.AuthenticationError:
        sys.exit("❌ Clé refusée ou absente. Vérifiez la variable ANTHROPIC_API_KEY\n"
                 "   (fiche « Mise en route — clé API »). Sous VS Code, fermez et rouvrez\n"
                 "   l'éditeur après avoir créé la variable.")
    except (anthropic.PermissionDeniedError, anthropic.NotFoundError):
        sys.exit(f"❌ Modèle refusé. Seul « {MODELE} » est ouvert sur votre compte.")
    except anthropic.RateLimitError:
        sys.exit("❌ Trop de requêtes, ou plafond mensuel de l'équipe atteint.\n"
                 "   Réessayez plus tard, et prévenez votre enseignant si ça persiste.")
    except anthropic.BadRequestError as e:
        sys.exit(f"❌ Requête refusée : {e}\n"
                 "   Si le message parle de crédit ou de limite, prévenez votre enseignant.")
    except anthropic.APIConnectionError:
        sys.exit("❌ Impossible de joindre l'API. Vérifiez votre connexion Internet.")

    # --- 1. La réponse, et surtout le COMPTE des tokens -----------------------
    texte = next((b.text for b in reponse.content if b.type == "text"), "")
    t_entree = reponse.usage.input_tokens    # ce que vous avez envoyé (votre question)
    t_sortie = reponse.usage.output_tokens   # ce que Claude a écrit (sa réponse)
    total = t_entree + t_sortie

    print("\nQuestion :", question)
    print("\nRéponse de Claude :\n" + texte)
    print(f"\nTokens consommés — entrée : {t_entree} · sortie : {t_sortie} · total : {total}")
    print("👉 C'est ce total qui va dans la colonne « Tokens » de votre journal.")

    # --- 2. L'impact calculé par EcoLogits, s'il est disponible ---------------
    impacts = getattr(reponse, "impacts", None)
    if ecologits_actif and impacts is not None:
        def lisible(v):
            # Selon la version d'EcoLogits, une valeur est un nombre OU une fourchette.
            return f"{fr(v.min)} à {fr(v.max)}" if hasattr(v, "min") else fr(v)
        print("\n--- Estimation par EcoLogits (bibliothèque spécialisée) ---")
        print(f"  Énergie : {lisible(impacts.energy.value)} {impacts.energy.unit}")
        print(f"  CO₂e    : {lisible(impacts.gwp.value)} {impacts.gwp.unit}")
        print("  (EcoLogits utilise ses propres hypothèses : comparez-les aux nôtres.)")
    elif ecologits_actif:
        print("\n[info] EcoLogits ne connaît pas ce modèle : seul le calcul à la main suit.")

    # --- 3. Le même appel, estimé à la main -----------------------------------
    afficher_empreinte(total)


# =========================================================================
# MODE 2 — Le bilan de fin de projet
# =========================================================================
def bilan(total_tokens):
    print("=" * 72)
    print("BILAN DE VOTRE USAGE DE L'IA — à reporter dans la synthèse de votre journal")
    print("=" * 72)
    afficher_empreinte(total_tokens)
    print("\n  N'oubliez pas le PÉRIMÈTRE : ce total ne compte que les usages dont vous")
    print("  connaissez les tokens (le compte fourni). Un usage de ChatGPT, Gemini ou")
    print("  Copilot n'expose pas ses tokens : dites-le dans votre synthèse. Annoncer ce")
    print("  qu'on n'a pas pu mesurer fait partie d'une mesure honnête.")


# =========================================================================
if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--bilan":
        if len(args) < 2 or not args[1].replace(" ", "").isdigit():
            sys.exit("Usage : python 17-poc-empreinte-ia.py --bilan <nombre total de tokens>")
        bilan(int(args[1].replace(" ", "")))
    else:
        demonstration(" ".join(args) or
                      "Explique en 3 phrases ce qu'est une base de données relationnelle.")
