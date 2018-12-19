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
        esperados = self._obtener_prop_guias(nombre_guia, "salida_esperada")
        assert len(codigos) == len(archivos)
        trabajo = []
        for i in range(len(codigos)):
            trabajo.append({
                "archivo_datos": archivos[i],
                "codigo": codigos[i],
                "salida_esperada": esperados[i]
            })
        return trabajo

    def correr_trabajo(self, trabajo, tipo):
        """Corre una instancia de docker pasando `trabajo` como json.
        El tipo de worker que se corre depende de tipo.
        `trabajo` es una lista de diccionarios con keys entradas
        archivo_entrada y codigo.
        e.g. [{"archivo_datos": "dataframe1.csv", "codigo": "datos = datos"}]
        Devuelve una lista con el resultado (OK, o error) de cada ejercicio.
        """
        worker = subprocess.Popen(["docker", "run", "-i", "worker", tipo.lower()],
                stdin = subprocess.PIPE, stdout = subprocess.PIPE,
                stderr = subprocess.PIPE)
        outs, errs = worker.communicate(json.dumps(trabajo).encode("utf-8"))

        return self.calcular_diffs(trabajo, json.loads(outs))

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
        columnas a listas de valores."""
        if len(salida["error"]) > 0:
            return "El corrector devolvió un error: %s".format(
                salida[j]["error"])

        with open("guias/salidas/" + ejercicio["salida_esperada"]) as f:
            esperado = json.loads(f.read())
        obtenido = json.loads(salida["output"])
        respuesta = ""
        # Revisamos que las dimensiones sean las esperadas.
        print(obtenido)
        columnas_obtenidas = list(obtenido.keys())
        columnas_esperadas = list(esperado.keys())
        if len(columnas_obtenidas) != len(columnas_esperadas):
            respuesta = "La salida tiene {} columnas y se esperaban {}. ".format(
                len(columnas_obtenidas), len(columnas_esperadas)
                )
        if len(obtenido[columnas_obtenidas[0]]) != len(esperado[columnas_esperadas[0]]):
            respuesta = "La salida tiene {} filas y se esperaban {}.".format(
                len(obtenido[columnas_obtenidas[0]]), len(esperado[columnas_esperadas[0]]))

        if len(respuesta) > 0:
            return respuesta

        if obtenido.keys() != esperado.keys():
            # (comparamos .keys() porque es invariante a orden)
            return "Se esperaban columnas con los nombres: '{}'".format(
                ",".join(columnas_esperadas))

        # Las dimensiones están OK, ahora podemos comparar los valores.
        for col, valores_esperados in esperado.items():
            valores_obtenidos = obtenido[col]
            for j in range(len(valores_esperados)):
                esp, obt = valores_esperados[str(j)], valores_obtenidos[str(j)]
                if type(esp) != type(obt):
                    return "En la columna {} se vio el tipo {} y se esperaba {}".format(
                        col, type(obt).__name__, type(esp).__name__)
                if not self._son_iguales(obt, esp):
                    return "En la columna {} se vio el valor {} y se esperaba {}".format(
                        col, str(obt), str(esp))
        return "Todo OK!"

    def calcular_diffs(self, trabajo, salida):
        """Para cada ejercicio en trabajo, revisamos que la salida sea correcta;
        esto es, que el JSON coincida con la salida esperada."""
        respuestas = [self.calcular_diff(trabajo[j], salida[j])
            for j in range(len(trabajo))]
        return respuestas
