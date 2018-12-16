import yaml
import os
import json
import subprocess

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

    def _obtener_prop_guias(self, titulo, prop):
        for guia in self.guias:
            if guia["titulo"] == titulo:
                return [ej[prop] for ej in guia["ejercicios"]]

    def enunciados_de(self, titulo):
        return self._obtener_prop_guias(titulo, "enunciado")

    def preparar_trabajo(self, codigos, nombre_guia):
        archivos = self._obtener_prop_guias(nombre_guia, "archivo_entrada")
        assert len(codigos) == len(archivos)
        trabajo = []
        for i in range(len(codigos)):
            trabajo.append({
                "archivo_datos": archivos[i],
                "codigo": codigos[i]
                })
        return trabajo

    def correr_trabajo(self, trabajo, tipo):
        """Corre una instancia de docker pasando `trabajo` como json.
        El tipo de worker que se corre depende de tipo.
        `trabajo` es una lista de diccionarios con keys entradas
        archivo_entrada y codigo.
        e.g. [{"archivo_datos": "dataframe1.csv", "codigo": "datos = datos"}]
        """
        worker = subprocess.Popen(["docker", "run", "-i", "worker", tipo.lower()],
                stdin = subprocess.PIPE, stdout = subprocess.PIPE,
                stderr = subprocess.PIPE)
        outs, errs = worker.communicate(json.dumps(trabajo).encode("utf-8"))
        return json.loads(outs)
