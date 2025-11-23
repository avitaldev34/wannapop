from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LoginForm, RegisterForm
from .extensions import db
from .models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Ruta de Login
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Aquí faríem la comprovació de l'usuari i contrasenya
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            flash("Sessió iniciada correctament!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Credencials incorrectes", "danger")
    return render_template("auth/login.html", form=form)

# Ruta de Registre
@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Crear un nou usuari
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,  # ⚠️ En un projecte real, cal encriptar la contrasenya!
            avatar=form.avatar.data.filename if form.avatar.data else None
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Usuari registrat correctament!", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)
