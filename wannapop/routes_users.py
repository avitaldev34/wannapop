from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os

from wannapop.extensions import db
from wannapop.models import User, Role
from wannapop.forms import UserForm

bp_users = Blueprint("users", __name__)

# Carpeta de subida de avatares
UPLOAD_FOLDER = os.path.join("wannapop", "static", "uploads")
DEFAULT_AVATAR = "user_default.jpg"  # imagen por defecto

# ------------------------------
# USERS
# ------------------------------

@bp_users.route("/users")
def list_users():
    """
    Llista tots els usuaris.
    """
    users = User.query.all()
    return render_template("users/list_users.html", users=users)


@bp_users.route("/users/<int:id>")
def read_user(id):
    """
    Mostra el detall d'un usuari.
    """
    user = User.query.get_or_404(id)
    return render_template("users/read_user.html", user=user)


@bp_users.route("/users/create", methods=["GET", "POST"])
def create_user():
    """
    Crea un nou usuari amb rol seleccionable.
    """
    form = UserForm()
    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]

    if not roles:
        flash("Has de crear rols abans de poder crear usuaris.", "warning")
        return redirect(url_for("users.list_users"))

    if form.validate_on_submit():
        filename = DEFAULT_AVATAR
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.avatar.data.save(filepath)

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method="scrypt"),  # ✅ hash seguro
            avatar=filename,
            role_id=form.role_id.data
        )
        db.session.add(user)
        db.session.commit()
        flash("Usuari creat correctament!", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/create.html", form=form)


@bp_users.route("/users/update/<int:id>", methods=["GET", "POST"])
def update_user(id):
    """
    Actualitza un usuari existent.
    """
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.role_id = form.role_id.data

        # Solo rehashear si se ha introducido nueva contraseña
        if form.password.data:
            user.password = generate_password_hash(form.password.data, method="scrypt")

        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.avatar.data.save(filepath)
            user.avatar = filename
        elif not user.avatar:
            # si no tiene avatar, poner el default
            user.avatar = DEFAULT_AVATAR

        db.session.commit()
        flash("Usuari actualitzat correctament!", "success")
        return redirect(url_for("users.read_user", id=user.id))

    return render_template("users/update.html", form=form, user=user)


@bp_users.route("/users/delete/<int:id>", methods=["GET", "POST"])
def delete_user(id):
    """
    Elimina un usuari i els seus productes associats.
    """
    user = User.query.get_or_404(id)
    if request.method == "POST":
        # eliminar productos asociados
        for product in user.products:
            db.session.delete(product)

        db.session.delete(user)
        db.session.commit()
        flash(f"Usuari '{user.name}' eliminat correctament!", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/delete.html", user=user)
