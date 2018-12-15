import yaml
import os
import yaml

class Corrector:
    def __init__(self):
        self.cargar_guias()

    def cargar_guias(self):
        archivos = os.listdir("guias/")
        self.guias = []
        for archivo in archivos:
            if archivo[-4:] != ".yml":
                continue
            with open("guias/" + archivo) as f:
                guia = yaml.load(f)
                self.guias.append(guia)

    def nombres_guias(self):
        return [guia["titulo"] for guia in self.guias]

    def enunciados_de(self, titulo):
        for guia in self.guias:
            if guia["titulo"] == titulo:
                return [ej["enunciado"] for ej in guia["ejercicios"]]
