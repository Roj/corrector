from flask import Flask, render_template
from corrector import Corrector
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
