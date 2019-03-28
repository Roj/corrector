from worker import Worker
import pandas as pd
import logging
import time as time

logger = logging.getLogger()
class PandasWorker(Worker):
    def __init__(self):
        super().__init__()
        self.dataframe_cache = {}

    def preparar_codigo(self, codigo, num_archivos):
        if num_archivos > 1:
            args_archivos = ["datos" + str(i+1)
                    for i in range(num_archivos)]
        else:
            args_archivos = ["datos"]
        args_archivos = ",".join(args_archivos)

        codigo = ["\t" + linea for linea in codigo.split("\n")]
        codigo = (["def programa(pd, {}):".format(args_archivos)]
                + codigo
                + ["\treturn datos"])
        return "\n".join(codigo)

    def agregar_resultado(self, output="", error=""):
        self.resultados.append({"output": output, "error": error})

    def _cargar_de_cache(self, ar):
        # Para evitar leer de disco cada vez, cargamos una
        # sola vez y el resto hacemos una copia en memoria.
        if ar not in self.dataframe_cache:
            df = pd.read_csv("datos/"+ar, sep=None)
            self.dataframe_cache[ar] = df.copy()

        return self.dataframe_cache[ar].copy()
    def correr_trabajo(self, ejercicios):
        self.resultados = []
        modulo = None
        start_time = time.time()
        for ejercicio in ejercicios:
            codigo = ejercicio["codigo"]
            if not Worker.codigo_es_seguro(codigo):
                self.agregar_resultado(
                    error = "Código no seguro o con errores de sintaxis."
                )
                continue
            # Preparamos los datos y el código.
            archivos = ejercicio["archivos_entrada"].split(",")
            datos = [self._cargar_de_cache(ar) for ar in archivos]
            codigo = self.preparar_codigo(codigo, len(archivos))
            # Cargamos el código y lo corremos.
            modulo = Worker.cargar_como_modulo(codigo)
            try:
                # Corremos modulo.programa(pd, datos[0], datos[1], ...)
                output = eval("modulo.programa(pd, {})".format(
                    ",".join(["datos[{}]".format(i) for i in range(len(datos))])
                ))
                # Evitamos mandar mucha data. 
                output = output.head(500)
                self.agregar_resultado(
                    output = output.to_json()
                )
            except Exception as e:
                self.agregar_resultado(
                    error = "Error en el código: " + str(e)
                )
        end_time = time.time()
        logger.debug("Tiempo de servir la peticion:{}".format(end_time-start_time))
        return self.resultados
