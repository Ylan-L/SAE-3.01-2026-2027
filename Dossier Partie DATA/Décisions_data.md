Décision n°1 : seuil de gel strict (<)

Un jour de gel est un jour où t_min < seuil_gel_c. Une journée dont la température minimale est exactement égale au seuil n’est pas comptée.
Pourquoi : c’est la définition inscrite dans le schéma de dim_culture, appliquée à l’identique dans le SQL (t_min < k.seuil_gel_c) et dans indicateurs.py. Une seule règle partout évite que le SQL et le Python donnent deux résultats différents.
Impact mesuré : à Reims, 3 jours ont une température minimale d’exactement 0,0 °C en avril-mai (2001, 2041, 2043). Avec <, Reims compte 5 jours de gel sur 2001-2003 (1,7 par an) et 0 sur 2041-2043. Avec ≤, elle en compterait 6 (2 par an) puis 2 (0,7 par an). Le choix ne change pas le sens de l’évolution, mais il change le niveau annoncé pour 2041-2043.
Test associé : test_gel_seuil_strict_et_moyenne_sur_horizon.
Limite : le seuil de chaque culture est lui-même une approximation (il dépend du stade et de la variété), d’un ordre comparable à l’écart entre < et <=