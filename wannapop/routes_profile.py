from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from wannapop.extensions import db
from wannapop.models import Product, User
from werkzeug.utils import secure_filename
import os

bp_profile = Blueprint("profile", __name__)

UPLOAD_FOLDER = os.path.join("wannapop", "static", "uploads")

@bp_profile.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    """
    Mostra el perfil de l'usuari autenticat.
    - Nom, email, rol.
    - Estat de bloqueig (si està bloquejat).
    - Si és wanner: llistat de productes (incloent bloquejats).
    - Permet canviar nom i avatar.
    """
    user = current_user

    if request.method == "POST":
        # Actualitzar nom i avatar
        new_name = request.form.get("name", "").strip()
        if new_name:
            user.name = new_name

        if "avatar" in request.files and request.files["avatar"].filename:
            avatar_file = request.files["avatar"]
            filename = secure_filename(avatar_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            avatar_file.save(filepath)
            user.avatar = filename

        db.session.commit()
        flash("Perfil actualitzat correctament!", "success")
        return redirect(url_for("profile.profile"))

    # Si és wanner, agafem els seus productes
    products = []
    if user.role.name == "wanner":
        products = Product.query.filter_by(seller_id=user.id).all()

    return render_template("profile/profile.html", user=user, products=products)
