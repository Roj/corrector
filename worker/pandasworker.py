from worker import Worker
import pandas as pd

class PandasWorker(Worker):
    def __init__(self, ejercicios):
        super().__init__(ejercicios)
        self.resultados = []

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

    def correr(self):
        modulo = None
        for ejercicio in self.ejercicios:
            codigo = ejercicio["codigo"]
            if not Worker.codigo_es_seguro(codigo):
                self.agregar_resultado(
                    error = "Código no seguro o con errores de sintaxis."
                )
                continue
            # Preparamos los datos y el código.
            archivos = ejercicio["archivos_datos"].split(",")
            datos = [pd.read_csv("datos/"+ar) for ar in archivos]
            codigo = self.preparar_codigo(codigo, len(archivos))
            # Cargamos el código y lo corremos.
            modulo = Worker.cargar_como_modulo(codigo, modulo)
            re_importar = True
            try:
                # Corremos modulo.programa(pd, datos[0], datos[1], ...)
                output = eval("modulo.programa(pd, {})".format(
                    ",".join(["datos[{}]".format(i) for i in range(len(datos))])
                ))
                self.agregar_resultado(
                    output = output.to_json()
                )
            except Exception as e:
                self.agregar_resultado(
                    error = "Error en el código: " + str(e)
                )

    def respuestas(self):
        return self.resultados
