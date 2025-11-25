from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager
from .forms import LoginForm, RegisterForm
from .models import User, Role, BlockedUser   
from werkzeug.utils import secure_filename
import os

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Carpeta de pujada d’avatars
UPLOAD_FOLDER = os.path.join("wannapop", "static", "uploads")
DEFAULT_AVATAR = "user_default.jpg"

# ------------------------------
# Configuració Flask-Login
# ------------------------------
@login_manager.user_loader
def load_user(user_id):
    """Carrega l'usuari per id per a mantenir la sessió"""
    return User.query.get(int(user_id))


# ------------------------------
# Ruta: Login (GET | POST)
# ------------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("Ja has iniciat sessió.", "info")
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        # Comprovem si l’usuari existeix i contrasenya correcta
        if user and check_password_hash(user.password, form.password.data):
            # Impedir login si l’usuari està bloquejat
            if user.blocked:
                flash(f"No pots iniciar sessió: Usuari bloquejat. Raó: {user.blocked.reason}", "danger")
                return redirect(url_for("auth.login"))

            login_user(user)
            flash("Has iniciat sessió correctament.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.index"))
        else:
            flash("Credencials incorrectes. Torna-ho a intentar.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html", form=form)


# ------------------------------
# Ruta: Register (GET | POST)
# ------------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("Ja tens la sessió iniciada.", "info")
        return redirect(url_for("main.index"))

    form = RegisterForm()

    # Omplir desplegable amb rols de la BD
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Ja existeix un usuari amb aquest correu.", "warning")
            return redirect(url_for("auth.register"))

        # Validar rol seleccionat
        selected_role = Role.query.get(form.role.data)
        if not selected_role:
            flash("El rol seleccionat no existeix.", "danger")
            return redirect(url_for("auth.register"))

        # Guardar contrasenya hasheada
        password_hash = generate_password_hash(form.password.data, method="scrypt")

        new_user = User(
            name=form.name.data.strip(),
            email=email,
            password=password_hash,
            role_id=selected_role.id,
            avatar=DEFAULT_AVATAR
        )

        # Guardar avatar si es puja
        if hasattr(form, "avatar") and form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.avatar.data.save(filepath)
            new_user.avatar = filename

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Usuari registrat correctament. Ara pots iniciar sessió.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Hi ha hagut un error en crear l'usuari: {e}", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html", form=form)


# ------------------------------
# Ruta: Logout (POST)
# ------------------------------
@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Has tancat la sessió correctament.", "success")
    return redirect(url_for("auth.login"))
