from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager
from .forms import LoginForm, RegisterForm
from .models import User, Role, BlockedUser
from werkzeug.utils import secure_filename
import os
import secrets
import smtplib
from email.mime.text import MIMEText

# Importem el helper per establir identitat de rols
from .helper_role import set_identity_on_login  

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

            # Nova comprovació: només permetre login si verificat
            if user.verified == 0:
                flash("Has de verificar el teu correu abans de fer login. Revisa la bústia.", "warning")
                return redirect(url_for("main.index"))

            # Login correcte
            login_user(user)
            set_identity_on_login(current_app, user)

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
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Ja existeix un usuari amb aquest correu.", "warning")
            return redirect(url_for("auth.register"))

        selected_role = Role.query.get(form.role.data)
        if not selected_role:
            flash("El rol seleccionat no existeix.", "danger")
            return redirect(url_for("auth.register"))

        password_hash = generate_password_hash(form.password.data, method="scrypt")

        # Generem token i marquem com no verificat
        token = secrets.token_urlsafe(20)
        new_user = User(
            name=form.name.data.strip(),
            email=email,
            password=password_hash,
            role_id=selected_role.id,
            avatar=DEFAULT_AVATAR,
            email_token=token,
            verified=0
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

            # Enviem correu de verificació
            sender = os.getenv("MAIL_SENDER_ADDR")
            password_mail = os.getenv("MAIL_SENDER_PASSWORD")
            smtp_server = os.getenv("MAIL_SMTP_SERVER")
            smtp_port = int(os.getenv("MAIL_SMTP_PORT", 587))

            verify_link = url_for("auth.verify", user_id=new_user.id, email_token=token, _external=True)
            msg = MIMEText(f"Benvingut {new_user.name}! Verifica el teu correu clicant aquí: {verify_link}", "plain", "utf-8")
            msg["Subject"] = "Verificació de correu Wannapop"
            msg["From"] = sender
            msg["To"] = email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password_mail)
                server.sendmail(sender, [email], msg.as_string())

            flash("Usuari registrat! Revisa el teu correu per verificar l'adreça.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error en registre: {e}")
            flash(f"Hi ha hagut un error en crear l'usuari.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html", form=form)


# ------------------------------
# Ruta: Verify (GET)
# ------------------------------
@bp.route("/verify/<int:user_id>/<email_token>")
def verify(user_id, email_token):
    """Verifica l'usuari si el token coincideix"""
    user = User.query.filter_by(id=user_id, email_token=email_token).first()
    if user:
        user.verified = 1
        user.email_token = None
        db.session.commit()
        flash("Verificació correcta! Ja pots fer login.", "success")
        return redirect(url_for("auth.login"))
    else:
        flash("Error de verificació. Torna-ho a provar.", "danger")
        return redirect(url_for("main.index"))


# ------------------------------
# Ruta: Resend (GET | POST)
# ------------------------------
@bp.route("/resend", methods=["GET", "POST"])
def resend():
    """Permet reenviar correu de verificació a usuaris no verificats"""
    if current_user.is_authenticated:
        flash("Ja tens sessió iniciada.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.verified == 0:
            token = secrets.token_urlsafe(20)
            user.email_token = token
            db.session.commit()

            verify_link = url_for("auth.verify", user_id=user.id, email_token=token, _external=True)
            sender = os.getenv("MAIL_SENDER_ADDR")
            password_mail = os.getenv("MAIL_SENDER_PASSWORD")
            smtp_server = os.getenv("MAIL_SMTP_SERVER")
            smtp_port = int(os.getenv("MAIL_SMTP_PORT", 587))

            msg = MIMEText(f"Hola! Torna a verificar el teu correu clicant aquí: {verify_link}", "plain", "utf-8")
            msg["Subject"] = "Reenviament verificació Wannapop"
            msg["From"] = sender
            msg["To"] = email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password_mail)
                server.sendmail(sender, [email], msg.as_string())

            flash("Nou correu de verificació enviat!", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("No s'ha trobat usuari o ja està verificat.", "danger")
            return redirect(url_for("auth.resend"))

    return render_template("auth/resend.html")


# ------------------------------
# Ruta: Logout (POST)
# ------------------------------
@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Has tancat la sessió correctament.", "success")
    return redirect(url_for("auth.login"))
