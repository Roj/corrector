#!/usr/bin/python3
from subprocess import call
import os

archivos = os.listdir("guias/entradas")

def bajar_si_no_existe(archivo, url):
    if archivo not in archivos:
        print("Descargamos el dataset {}...".format(url))
        call([
            "wget",
            url,
            "-O",
            "guias/entradas/" + archivo])
    else:
        print("Ya tenemos el dataset {}, salteamos...".format(archivo))

bajar_si_no_existe("calidad-de-aire-2017.csv", 
            "http://cdn.buenosaires.gob.ar/datosabiertos/datasets/calidad-de-aire/calidad-de-aire-2017.csv")

bajar_si_no_existe("departamentos-en-venta-2013.csv",
            "http://cdn.buenosaires.gob.ar/datosabiertos/datasets/departamentos-en-venta/departamentos-en-venta-2013.csv")

bajar_si_no_existe("departamentos-en-venta-2016.csv", 
            "http://cdn.buenosaires.gob.ar/datosabiertos/datasets/departamentos-en-venta/departamentos-en-venta-2016.csv")
