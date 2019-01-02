import yaml
import os
import json
import logging
import socket

BUFFER_SIZE = 1024
WORKER_HOST = "127.0.0.1"
WORKER_PORT = 6000

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

    def nombre_parametro_de(self, titulo):
        return self.guias[titulo]["nombre_parametro"]

    def preparar_trabajo(self, codigos, nombre_guia):
        archivos = [ej["archivos_entrada"] for ej in self.guias[nombre_guia]["ejercicios"]]
        esperados = [ej["salida_esperada"] for ej in self.guias[nombre_guia]["ejercicios"]]
        assert len(codigos) == len(archivos)
        trabajo = []
        for i in range(len(codigos)):
            trabajo.append({
                "archivos_entrada": archivos[i],
                "codigo": codigos[i],
                "salida_esperada": esperados[i]
            })
        return trabajo

    def correr_trabajo(self, trabajo, tipo):
        """Corre una instancia de docker pasando `trabajo` como json.
        El tipo de worker que se corre depende de tipo.
        `trabajo` es una lista de diccionarios con keys entradas
        archivo_entrada y codigo.
        e.g. [{"archivos_entrada": "dataframe1.csv", "codigo": "datos = datos"}]
        archivos_entrada puede representar varios archivos si se separan con
        comas (cuidado con los espacios).
        Devuelve una lista con el resultado (OK, o error) de cada ejercicio.
        """
        trabajo = {"guia": tipo.lower(), "ejercicios": trabajo}
        self.logger.debug("Enviando a docker: {}".format(json.dumps(trabajo)))

        # Iniciamos un socket estilo HTTP (un solo request, un solo response)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((WORKER_HOST, WORKER_PORT))
        sock.sendall(json.dumps(trabajo).encode("utf-8"))
        sock.shutdown(socket.SHUT_WR) # Avisamos que no vamos a escribir más.

        respuesta = b""
        buffer = sock.recv(BUFFER_SIZE)
        while len(buffer) > 0:
            respuesta += buffer
            buffer = sock.recv(BUFFER_SIZE)
        respuesta = respuesta.decode("utf-8")
        sock.close()

        self.logger.debug("Respuesta de docker: {}".format(respuesta))
        return json.dumps(self.calcular_diffs(trabajo["ejercicios"],
            json.loads(respuesta)))

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
