from flask import Blueprint, render_template

# Definimos el blueprint principal
bp = Blueprint("main", __name__)

# Ruta principal "/"
@bp.route("/")
def index():
    # Renderiza la plantilla base o la página de inicio
    return render_template("layout/_base.html")

# Ruta de prueba "/hello"
@bp.route("/hello")
def hello():
    return "<h1>Hello, Wannapop!</h1>"
