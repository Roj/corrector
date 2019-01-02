from flask import Flask, render_template, request
from corrector import Corrector
import json
import logging
app = Flask(__name__)

corrector = Corrector()
if app.debug:
    corrector.logger.setLevel(logging.DEBUG)

@app.route("/")
def home():
    return render_template("home.html",
        guias = corrector.nombres_guias())

@app.route("/guia/<titulo>")
def mostrar_guia(titulo):
    assert titulo in corrector.nombres_guias()
    # Definimos los parámetros de datos para los ejercicios.
    ejercicios = corrector.ejercicios_de(titulo)
    params = []
    for ejercicio in ejercicios:
        nparams = len(ejercicio["archivos_entrada"].split(","))
        if nparams == 1:
            params.append("datos")
        else:
            # "datos1, datos2, ..."
            params.append(", ".join(["datos"+str(i+1) for i in range(nparams)]))

    return render_template("guia.html",
        guias = corrector.nombres_guias(),
        guia_actual = titulo,
        ejercicios = ejercicios,
        params = params,
        nombre_param = corrector.nombre_parametro_de(titulo))

@app.route("/guia/<titulo>/entregar", methods=["POST"])
def entregar_guia(titulo):
    """Recibe una lista de códigos de la guía como JSON."""
    assert titulo in corrector.nombres_guias()
    assert request.is_json
    codigos = request.get_json()
    trabajo = corrector.preparar_trabajo(codigos, titulo)

    return json.dumps(corrector.correr_trabajo(trabajo, titulo)), 200
