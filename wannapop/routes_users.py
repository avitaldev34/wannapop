from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
import logging
import os
from werkzeug.utils import secure_filename
from wannapop.models import User, db
from wannapop.forms import UserForm

bp = Blueprint("users", __name__, url_prefix="/users")
logger = logging.getLogger(__name__)

# Ruta: /users/list
@bp.route("/list")
def list_users():
    users = User.query.all()
    logger.debug(f"Se han recuperado {len(users)} usuarios de la BD")
    return render_template("users/list_users.html", users=users)

# Ruta: /users/read/<id>
@bp.route("/read/<int:user_id>")
def read_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        logger.warning(f"Usuario con id {user_id} no encontrado")
        abort(404)
    return render_template("users/read_users.html", user=user)

# Ruta: /users/create
@bp.route("/create", methods=["GET", "POST"])
def create_user():
    form = UserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            avatar_filename = None

            if form.avatar.data:
                filename = secure_filename(form.avatar.data.filename)
                uploads_dir = current_app.config["UPLOAD_FOLDER"]
                os.makedirs(uploads_dir, exist_ok=True)
                avatar_path = os.path.join(uploads_dir, filename)
                form.avatar.data.save(avatar_path)
                avatar_filename = filename

            # Imagen por defecto si no se sube ninguna
            if not avatar_filename or avatar_filename.strip() == "":
                avatar_filename = "user_default.jpg"


            new_user = User(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data,
                avatar=avatar_filename
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Usuari creat correctament!", "success")
            return redirect(url_for("users.list_users"))
        else:
            flash("Errors en el formulari", "danger")

    return render_template("users/create.html", form=form)

# Ruta: /users/update/<id>
@bp.route("/update/<int:user_id>", methods=["GET", "POST"])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    form = UserForm(obj=user)

    if request.method == "POST":
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.password = form.password.data

            if form.avatar.data:
                filename = secure_filename(form.avatar.data.filename)
                uploads_dir = current_app.config["UPLOAD_FOLDER"]
                os.makedirs(uploads_dir, exist_ok=True)
                avatar_path = os.path.join(uploads_dir, filename)
                form.avatar.data.save(avatar_path)
                user.avatar = filename

            # Imagen por defecto si no tiene ninguna
            if not user.avatar:
                user.avatar = "user_default.png"

            db.session.commit()
            flash("Usuari actualitzat correctament!", "success")
            return redirect(url_for("users.list_users"))
        else:
            flash("Errors en el formulari", "danger")

    return render_template("users/update.html", form=form, user=user)

# Ruta: /users/delete/<id>
@bp.route("/delete/<int:user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        flash("Usuari eliminat correctament!", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/delete.html", user=user)
