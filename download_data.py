#!/usr/bin/python3
from subprocess import call
import os

archivos = os.listdir("guias/entradas")

if "calidad-de-aire-2017.csv" not in archivos:
    print("Descargamos el dataset de calidad de aire...")
    call([
        "wget",
        "https://data.buenosaires.gob.ar/api/files/calidad-de-aire-2017.csv/download/csv",
        "-O",
        "guias/entradas/calidad-de-aire-2017.csv"])
else:
    print("Ya tenemos el dataset de calidad de aire, salteamos...")
