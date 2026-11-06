from openmeteo_client import recuperer_serie

serie = recuperer_serie(1, 50.63, 3.06, "2020-07-01", "2020-07-10")
print(len(serie), "jours")
print(serie[0])