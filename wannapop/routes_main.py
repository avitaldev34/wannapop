from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    # Vista principal
    return render_template("index.html", user=current_user)

@bp.route("/contact")
@login_required
def contact():
    """
    Pàgina de contacte.
    Accessible per qualsevol usuari autenticat.
    """
    return render_template("contact.html", user=current_user)
