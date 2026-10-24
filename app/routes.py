from flask import Blueprint
rutas = Blueprint('rutas', __name__)

@rutas.route('/')
def index():
    return "EcoReto conectado a Neon! Ya funciona."
