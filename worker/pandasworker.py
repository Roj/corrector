from worker import Worker
import pandas as pd

class PandasWorker(Worker):
    def __init__(self, ejercicios):
        super().__init__(ejercicios)
        self.resultados = []

    def preparar_codigo(self, codigo):
        codigo = ["\t" + linea for linea in codigo.split("\n")]
        codigo = ["def programa(pd, datos):"] + codigo + ["\treturn datos"]
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
            # Correr el código del alumno.
            codigo = self.preparar_codigo(codigo)
            modulo = Worker.cargar_como_modulo(codigo, modulo)
            re_importar = True
            datos = pd.read_csv("datos/"+ejercicio["archivo_datos"])
            try:
                output = modulo.programa(pd, datos)
                self.agregar_resultado(
                    output = output.to_json()
                )
            except Exception as e:
                self.agregar_resultado(
                    error = "Error en el código: " + str(e)
                )

    def respuestas(self):
        return self.resultados
