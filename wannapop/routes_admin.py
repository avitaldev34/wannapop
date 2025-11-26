from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from wannapop.extensions import db
from wannapop.models import User, Product

bp_admin = Blueprint("admin", __name__)

@bp_admin.route("/admin", methods=["GET","POST"])
@login_required
def admin():
    """
    Mostra llistat d'usuaris i productes bloquejats.
    Accessible només per admin i moderator.
    Permet desbloquejar múltiples usuaris/productes a la vegada.
    """
    if current_user.role.name not in ["admin","moderator"]:
        flash("No tens permisos per accedir a l'admin.", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        # Desbloquejar usuaris seleccionats
        user_ids = request.form.getlist("users")
        for uid in user_ids:
            user = User.query.get(int(uid))
            if user and user.blocked:
                db.session.delete(user.blocked)

        # Desbloquejar productes seleccionats
        product_ids = request.form.getlist("products")
        for pid in product_ids:
            product = Product.query.get(int(pid))
            if product and product.blocked:
                db.session.delete(product.blocked)

        db.session.commit()
        flash("Elements seleccionats desbloquejats correctament!", "success")
        return redirect(url_for("admin.admin"))

    blocked_users = User.query.filter(User.blocked != None).all()
    blocked_products = Product.query.filter(Product.blocked != None).all()

    return render_template("admin/admin.html", blocked_users=blocked_users, blocked_products=blocked_products)
