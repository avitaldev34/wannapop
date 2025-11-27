from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from wannapop.extensions import db
from wannapop.models import Product, User
from werkzeug.utils import secure_filename
import os
import secrets
import smtplib
from email.mime.text import MIMEText

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
    - Permet canviar nom, email i avatar.
    - Si es canvia el correu: es genera token, es marca com no verificat i s'envia correu de verificació.
    """
    user = current_user

    if request.method == "POST":
        # Actualitzar nom
        new_name = request.form.get("name", "").strip()
        if new_name:
            user.name = new_name

        # Actualitzar correu electrònic
        new_email = request.form.get("email", "").strip().lower()
        if new_email and new_email != user.email:
            user.email = new_email
            user.verified = 0  # marquem com no verificat
            token = secrets.token_urlsafe(20)
            user.email_token = token

            # Enviem correu de verificació
            sender = os.getenv("MAIL_SENDER_ADDR")
            password_mail = os.getenv("MAIL_SENDER_PASSWORD")
            smtp_server = os.getenv("MAIL_SMTP_SERVER")
            smtp_port = int(os.getenv("MAIL_SMTP_PORT", 587))

            verify_link = url_for("auth.verify", user_id=user.id, email_token=token, _external=True)
            msg = MIMEText(
                f"Has canviat el teu correu. Verifica'l clicant aquí: {verify_link}",
                "plain",
                "utf-8"
            )
            msg["Subject"] = "Verificació nou correu Wannapop"
            msg["From"] = sender
            msg["To"] = new_email

            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender, password_mail)
                    server.sendmail(sender, [new_email], msg.as_string())
                flash("Correu actualitzat! Revisa la bústia per verificar-lo.", "success")
            except Exception as e:
                current_app.logger.error(f"Error enviant email de verificació: {e}")
                flash("Error enviant correu de verificació.", "danger")

        # Actualitzar avatar
