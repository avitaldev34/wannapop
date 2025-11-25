from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint("main", __name__)

# ------------------------------
# Ruta principal "/"
# ------------------------------
@bp.route("/")
def index():
     # Si no està autenticat → login
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    # Si està autenticat → benvinguda
    return render_template("index.html", user=current_user)
# ------------------------------
# Ruta de prova "/hello"
# ------------------------------
@bp.route("/hello")
def hello():
    return "<h1>Hello, Wannapop!</h1>"
