from flask import Flask, render_template
from corrector import Corrector
app = Flask(__name__)

corrector = Corrector()

@app.route("/")
def home():
    return render_template("guia.html",
        guias = corrector.nombres_guias(),
        guia_actual = "Pandas",
        enunciados = corrector.enunciados_de("Pandas"))
