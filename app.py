from flask import Flask, render_template, request
from corrector import Corrector
import json
app = Flask(__name__)

corrector = Corrector()

@app.route("/")
def home():
    return render_template("home.html",
        guias = corrector.nombres_guias())

@app.route("/guia/<titulo>")
def mostrar_guia(titulo):
    assert titulo in corrector.nombres_guias()
    return render_template("guia.html",
        guias = corrector.nombres_guias(),
        guia_actual = titulo,
        enunciados = corrector.enunciados_de(titulo))

@app.route("/guia/<titulo>/entregar", methods=["POST"])
def entregar_guia(titulo):
    """Recibe una lista de códigos de la guía como JSON."""
    assert titulo in corrector.nombres_guias()
    assert request.is_json
    codigos = request.get_json()
    trabajo = corrector.preparar_trabajo(codigos, titulo)

    return json.dumps(corrector.correr_trabajo(trabajo, titulo)), 200
