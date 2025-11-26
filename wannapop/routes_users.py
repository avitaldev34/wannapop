from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os

from flask_login import login_required, current_user
from wannapop.extensions import db
from wannapop.models import User, Role
from wannapop.forms import UserForm

# Importem permisos de helper_role
from wannapop.helper_role import perm_read_users, perm_write_users

bp_users = Blueprint("users", __name__)

# Carpeta de pujada d’avatars
UPLOAD_FOLDER = os.path.join("wannapop", "static", "uploads")
DEFAULT_AVATAR = "user_default.jpg"  # imatge per defecte

# ------------------------------
# USERS
# ------------------------------

@bp_users.route("/users")
@login_required
def list_users():
    """
    Llista tots els usuaris.
    Accessible per wanner, moderator i admin.
    - wanner i moderator: només veuen usuaris wanner NO bloquejats.
    - admin: veu tots els usuaris.
    """
    if not perm_read_users.can():
        flash("No tens permisos per veure usuaris.", "danger")
        return redirect(url_for("main.index"))

    role = current_user.role.name
    if role in ["wanner", "moderator"]:
        # Filtrar només usuaris wanner no bloquejats
        users = (
            User.query.join(Role)
                      .filter(Role.name == "wanner", User.blocked == None)
                      .all()
        )
    else:  # admin
        users = User.query.all()

    return render_template("users/list_users.html", users=users)


@bp_users.route("/users/<int:id>")
@login_required
def read_user(id):
    """
    Mostra el detall d'un usuari.
    Accessible per wanner, moderator i admin.
    - wanner i moderator: només poden veure usuaris wanner NO bloquejats.
    - admin: pot veure qualsevol usuari.
    """
    if not perm_read_users.can():
        flash("No tens permisos per veure usuaris.", "danger")
        return redirect(url_for("main.index"))

    user = User.query.get_or_404(id)

    role = current_user.role.name
    if role in ["wanner", "moderator"]:
        if user.role.name != "wanner" or user.blocked:
            flash("No tens permisos per veure aquest usuari.", "danger")
            return redirect(url_for("users.list_users"))

    return render_template("users/read_user.html", user=user)


@bp_users.route("/users/create", methods=["GET", "POST"])
@login_required
def create_user():
    """
    Crea un nou usuari amb rol seleccionable.
    Només admin.
    """
    if not perm_write_users.can():
        flash("Només els administradors poden crear usuaris.", "danger")
        return redirect(url_for("users.list_users"))

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
            password=generate_password_hash(form.password.data, method="scrypt"),
            avatar=filename,
            role_id=form.role_id.data
        )
        db.session.add(user)
        db.session.commit()
        flash("Usuari creat correctament!", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/create.html", form=form)


@bp_users.route("/users/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_user(id):
    """
    Actualitza un usuari existent.
    Només admin amb restriccions:
    - No pot editar altres admins ni a si mateix.
    - No pot canviar el rol d’un usuari wanner.
    """
    if not perm_write_users.can():
        flash("Només els administradors poden modificar usuaris.", "danger")
        return redirect(url_for("users.read_user", id=id))

    user = User.query.get_or_404(id)

    # Admin no pot editar altres admins ni a si mateix
    if user.role.name == "admin" or user.id == current_user.id:
        flash("No pots modificar aquest usuari.", "danger")
        return redirect(url_for("users.read_user", id=id))

    form = UserForm(obj=user)
    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]

    if form.validate_on_submit():
        # Admin no pot canviar el rol d’un wanner
        if user.role.name == "wanner" and form.role_id.data != user.role_id:
            flash("No pots canviar el rol d’un usuari wanner.", "danger")
            return redirect(url_for("users.read_user", id=id))

        user.name = form.name.data
        user.email = form.email.data
        user.role_id = form.role_id.data

        if form.password.data:
            user.password = generate_password_hash(form.password.data, method="scrypt")

        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.avatar.data.save(filepath)
            user.avatar = filename
        elif not user.avatar:
            user.avatar = DEFAULT_AVATAR

        db.session.commit()
        flash("Usuari actualitzat correctament!", "success")
        return redirect(url_for("users.read_user", id=user.id))

    return render_template("users/update.html", form=form, user=user)


@bp_users.route("/users/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_user(id):
    """
    Elimina un usuari i els seus productes/bloqueig si existeix.
    Només admin amb restriccions:
    - No pot eliminar altres admins ni a si mateix.
    """
    if not perm_write_users.can():
        flash("Només els administradors poden eliminar usuaris.", "danger")
        return redirect(url_for("users.read_user", id=id))

    user = User.query.get_or_404(id)

    # Admin no pot eliminar altres admins ni a si mateix
    if user.role.name == "admin" or user.id == current_user.id:
        flash("No pots eliminar aquest usuari.", "danger")
        return redirect(url_for("users.read_user", id=id))

    if request.method == "POST":
        for product in user.products:
            db.session.delete(product)

        if user.blocked:
            db.session.delete(user.blocked)

        db.session.delete(user)
        db.session.commit()
        flash(f"Usuari '{user.name}' eliminat correctament!", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/delete.html", user=user)
