from worker import Worker
import json
import pyspark as sp
import logging

logger = logging.getLogger()
class SparkWorker(Worker):
    def __init__(self):
        self.context = sp.SparkContext(appName="SparkWorker")
        self.context.setLogLevel("ERROR")

    def preparar_codigo(self, codigo, num_archivos):
        if num_archivos > 1:
            args_archivos = ["datos" + str(i+1)
                    for i in range(num_archivos)]
        else:
            args_archivos = ["datos"]
        args_archivos = ",".join(args_archivos)

        codigo = ["\t" + linea for linea in codigo.split("\n")]
        codigo = (["def programa(context, {}):".format(args_archivos)]
                + codigo
                + ["\treturn datos"])
        return "\n".join(codigo)

    def agregar_resultado(self, output="", error=""):
        self.resultados.append({"output": output, "error": error})

    def cargar_archivo(self, archivo):
        with open(archivo, "r") as f:
            datos = json.loads(f.read())

        return self.context.parallelize(datos)

    def correr_trabajo(self, ejercicios):
        self.resultados = []
        modulo = None
        for ejercicio in ejercicios:
            codigo = ejercicio["codigo"]
            if not Worker.codigo_es_seguro(codigo):
                self.agregar_resultado(
                    error = "Código no seguro o con errores de sintaxis."
                )
                continue
            # Preparamos los datos y el código.
            archivos = ejercicio["archivos_entrada"].split(",")
            datos = [self.cargar_archivo("datos/"+ar) for ar in archivos]
            codigo = self.preparar_codigo(codigo, len(archivos))
            # Cargamos el código y lo corremos.
            modulo = Worker.cargar_como_modulo(codigo)
            try:
                # Corremos modulo.programa(pd, datos[0], datos[1], ...)
                logger.error("modulo.programa(self.context, {})".format(
                    ",".join(["datos[{}]".format(i) for i in range(len(datos))])
                ))
                output = eval("modulo.programa(self.context, {})".format(
                    ",".join(["datos[{}]".format(i) for i in range(len(datos))])
                ))
                self.agregar_resultado(
                    output = json.dumps(output.collect())
                )
            except Exception as e:
                self.agregar_resultado(
                    error = "Error en el código: " + str(e)
                )

        return self.resultados
