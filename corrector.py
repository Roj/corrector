import yaml
import os
import json
import subprocess
import logging

class Corrector:
    def __init__(self):
        self.cargar_guias()
        self.logger = logging.getLogger()
        self.logger.addHandler(logging.StreamHandler())
    def cargar_guias(self):
        archivos = os.listdir("guias/")
        self.guias = {}
        for archivo in archivos:
            if archivo[-4:] != ".yml":
                continue
            with open("guias/" + archivo) as f:
                guia = yaml.load(f)
                self.guias[guia["titulo"]] = guia

    def nombres_guias(self):
        return list(self.guias.keys())

    def ejercicios_de(self, titulo):
        return self.guias[titulo]["ejercicios"]

    def preparar_trabajo(self, codigos, nombre_guia):
        archivos = [ej["archivos_entrada"] for ej in self.guias[nombre_guia]["ejercicios"]]
        esperados = [ej["salida_esperada"] for ej in self.guias[nombre_guia]["ejercicios"]]
        assert len(codigos) == len(archivos)
        trabajo = []
        for i in range(len(codigos)):
            trabajo.append({
                "archivos_datos": archivos[i],
                "codigo": codigos[i],
                "salida_esperada": esperados[i]
            })
        return trabajo

    def correr_trabajo(self, trabajo, tipo):
        """Corre una instancia de docker pasando `trabajo` como json.
        El tipo de worker que se corre depende de tipo.
        `trabajo` es una lista de diccionarios con keys entradas
        archivo_entrada y codigo.
        e.g. [{"archivos_datos": "dataframe1.csv", "codigo": "datos = datos"}]
        archivos_datos puede representar varios archivos si se separan con
        comas (cuidado con los espacios).
        Devuelve una lista con el resultado (OK, o error) de cada ejercicio.
        """
        self.logger.debug("Enviando a docker: {}".format(json.dumps(trabajo)))
        worker = subprocess.Popen(["docker", "run", "-i", "worker", tipo.lower()],
                stdin = subprocess.PIPE, stdout = subprocess.PIPE,
                stderr = subprocess.PIPE)
        outs, errs = worker.communicate(json.dumps(trabajo).encode("utf-8"))
        self.logger.debug("Docker stdout: {}".format(outs))
        self.logger.debug("Docker stderr: {}".format(errs))
        return json.dumps(self.calcular_diffs(trabajo, json.loads(outs)))

    def _son_iguales(self, a, b):
        """Hace una comparación inteligente entre dos valores del mismo tipo"""
        if isinstance(a, str):
            return a == b
        if isinstance(a, float):
            return abs(a - b) < 0.01
        # Esperamos que sea int.
        return a == b

    def calcular_diff(self, ejercicio, salida):
        """Revisamos que no haya habido errores en la salida del Worker para
        cada ejercicio, y hacemos el diff de los json. El json mapea
        columnas a listas de valores.
        La respuesta es un dict con keys ("warning", "error", "info") y solo
        un valor seteado.
        """
        respuesta = {"warning": "", "error": "", "info": ""}
        if len(salida["error"]) > 0:
            respuesta["error"] = "El corrector devolvió un error: {}".format(
                salida["error"])
            return respuesta

        with open("guias/salidas/" + ejercicio["salida_esperada"]) as f:
            esperado = json.loads(f.read())
        obtenido = json.loads(salida["output"])
        # Revisamos que las dimensiones sean las esperadas.
        self.logger.debug("Obtenido:{}".format(obtenido))
        self.logger.debug("Esperado:{}".format(esperado))
        columnas_obtenidas = list(obtenido.keys())
        columnas_esperadas = list(esperado.keys())
        if len(columnas_obtenidas) != len(columnas_esperadas):
            respuesta["warning"] = "La salida tiene {} columnas y se esperaban {}. ".format(
                len(columnas_obtenidas), len(columnas_esperadas)
                )
        if len(obtenido[columnas_obtenidas[0]]) != len(esperado[columnas_esperadas[0]]):
            respuesta["warning"] = "La salida tiene {} filas y se esperaban {}.".format(
                len(obtenido[columnas_obtenidas[0]]), len(esperado[columnas_esperadas[0]]))

        if len(respuesta["warning"]) > 0:
            return respuesta

        if obtenido.keys() != esperado.keys():
            # (comparamos .keys() porque es invariante a orden)
            respuesta["warning"] = "Se esperaban columnas con los nombres: '{}'".format(
                ",".join(columnas_esperadas))
            return respuesta

        # Las dimensiones están OK, ahora podemos comparar los valores.
        for col, valores_esperados in esperado.items():
            valores_obtenidos = obtenido[col]
            for j in valores_obtenidos.keys():
                esp, obt = valores_esperados[j], valores_obtenidos[j]
                if type(esp) != type(obt):
                    respuesta["warning"] = "En la columna {} se vio el tipo {} y se esperaba {}".format(
                        col, type(obt).__name__, type(esp).__name__)
                    return respuesta
                if not self._son_iguales(obt, esp):
                    respuesta["warning"] = "En la columna {} se vio el valor {} y se esperaba {}".format(
                        col, str(obt), str(esp))
                    return respuesta
        respuesta["info"] = "Todo OK"
        return respuesta

    def calcular_diffs(self, trabajo, salida):
        """Para cada ejercicio en trabajo, revisamos que la salida sea correcta;
        esto es, que el JSON coincida con la salida esperada."""
        respuestas = [self.calcular_diff(trabajo[j], salida[j])
            for j in range(len(trabajo))]
        return respuestas
