# routes_auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager
from .forms import LoginForm, RegisterForm
from .models import User, Role

bp = Blueprint("auth", __name__, url_prefix="/auth")

# ------------------------------
# Configuració Flask-Login
# ------------------------------
@login_manager.user_loader
def load_user(user_id):
    # Carrega l'usuari per id per a mantenir la sessió
    return User.query.get(int(user_id))


# ------------------------------
# Ruta: Login (GET | POST)
# ------------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    # Si ja està autenticat, redirigim directament a l'inici
    if current_user.is_authenticated:
        flash("Ja has iniciat sessió.", "info")
        return redirect(url_for("main.index"))

    form = LoginForm()

    # Petició POST per validar credencials
    if form.validate_on_submit():
        # Buscar usuari per email
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        # Comprovació de contrasenya amb scrypt
        if user and check_password_hash(user.password, form.password.data):
            # Iniciar sessió de l'usuari
            login_user(user)
            flash("Has iniciat sessió correctament.", "success")

            # Redirecció a la pàgina d'inici
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.index"))
        else:
            # Credencials incorrectes
            flash("Credencials incorrectes. Torna-ho a intentar.", "danger")
            return redirect(url_for("auth.login"))

    # GET: mostrar la plantilla de login
    return render_template("auth/login.html", form=form)


# ------------------------------
# Ruta: Register (GET | POST)
# ------------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    # Si ja està autenticat, redirigim directament a l'inici
    if current_user.is_authenticated:
        flash("Ja tens la sessió iniciada.", "info")
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        # Normalitzar email
        email = form.email.data.strip().lower()

        # Comprovar si l'email ja existeix
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Ja existeix un usuari amb aquest correu.", "warning")
            return redirect(url_for("auth.register"))

        # Obtenir el rol per defecte 'wanner'
        default_role = Role.query.filter_by(name="wanner").first()
        if not default_role:
            # Si no existeix, el creem per assegurar que el registre funcioni
            default_role = Role(name="wanner")
            db.session.add(default_role)
            db.session.commit()

        # Generar hash de la contrasenya amb scrypt
        password_hash = generate_password_hash(form.password.data, method="scrypt")

        # Crear nou usuari
        new_user = User(
            name=form.name.data.strip(),
            email=email,
            password=password_hash,  # Guardem el hash, no la contrasenya en clar
            role_id=default_role.id
        )

        # Avatar opcional (si el formulari el proporciona)
        # Nota: la persistència del fitxer físic s'ha de gestionar al controlador de pujada (no aquí).
        if hasattr(form, "avatar") and form.avatar.data:
            # Guardem només el nom del fitxer o la ruta relativa, segons el teu flux de pujada
            new_user.avatar = form.avatar.data.filename

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Usuari registrat correctament. Ara pots iniciar sessió.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("Hi ha hagut un error en crear l'usuari. Revisa les dades.", "danger")
            return redirect(url_for("auth.register"))

    # GET: mostrar la plantilla de registre
    return render_template("auth/register.html", form=form)


# ------------------------------
# Ruta: Logout (POST)
# ------------------------------
@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    # Tancar la sessió de l'usuari autenticat
    logout_user()
    flash("Has tancat la sessió correctament.", "success")
    # Redirigir a la pàgina d’inici de sessió
    return redirect(url_for("auth.login"))
