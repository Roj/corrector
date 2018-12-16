from worker import Worker
import pandas as pd

class PandasWorker(Worker):
    def preparar_codigo(self, codigo):
        codigo = ["\t" + linea for linea in codigo.split("\n")]
        codigo = ["def programa(pd, datos):"] + codigo + ["\treturn datos"]
        return "\n".join(codigo)

    def correr(self):
        self.resultados = []
        modulo = None
        for ejercicio in self.ejercicios:
            codigo = ejercicio["codigo"]
            if not Worker.codigo_es_seguro(codigo):
                self.resultados.append({
                    "error": "Código no seguro.",
                    "output": ""
                })
                continue
            # Correr el código del alumno.
            codigo = self.preparar_codigo(codigo)
            modulo = Worker.cargar_como_modulo(codigo, modulo)
            re_importar = True
            datos = pd.read_csv(ejercicio["archivo_datos"])
            try:
                output = modulo.programa(pd, datos)
                self.resultados.append({
                    "error": "",
                    "output": output
                })
            except Exception as e:
                self.resultados.append({
                    "error": "Error en el código: " + str(e),
                    "output": ""
                })

    def respuestas(self):
        return self.resultados
