from flask import Blueprint, redirect, url_for, flash, request
from flask_login import current_user, login_required
from wannapop.extensions import db
from wannapop.models import Product, BlockedProduct

# Blueprint específic per moderació de productes
bp_block_products = Blueprint("block_products", __name__)

# ------------------------------
# Decorador per restringir rols
# ------------------------------
def roles_required(*roles):
    """
    Decorador per restringir accés a usuaris amb determinats rols.
    Exemple: @roles_required("moderator", "admin")
    """
    def wrapper(fn):
        from functools import wraps
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Has d'iniciar sessió per accedir.", "danger")
                return redirect(url_for("auth.login"))
            if current_user.role.name not in roles:
                flash("No tens permisos per fer aquesta acció.", "danger")
                return redirect(url_for("products.read_product", id=kwargs.get("product_id")))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


@bp_block_products.route("/products/<int:product_id>/block", methods=["POST"])
@login_required
@roles_required("moderator", "admin")   # ✅ només moderadors/admin poden bloquejar
def block_product(product_id):
    """
    Bloqueja un producte:
    - Comprova que el producte existeix.
    - No permet bloquejar si ja està bloquejat.
    - Crea el registre a blocked_products amb la raó i el moderador autenticat.
    - Retorna al read del producte amb missatge flash.
    """
    product = Product.query.get_or_404(product_id)

    # Comprovem si ja està bloquejat
    if product.blocked:
        flash("El producte ja està bloquejat.", "warning")
        return redirect(url_for("products.read_product", id=product_id))

    # Obtenim dades del formulari
    reason = request.form.get("reason", "").strip()
    if not reason:
        flash("Has d'indicar una raó per bloquejar el producte.", "danger")
        return redirect(url_for("products.read_product", id=product_id))

    # Moderador autenticat
    moderator_id = current_user.id

    # Creem el registre de bloqueig
    bloqueig = BlockedProduct(
        product_id=product.id,
        moderator_id=moderator_id,
        reason=reason
    )
    db.session.add(bloqueig)
    db.session.commit()

    flash("Producte bloquejat correctament.", "success")
    return redirect(url_for("products.read_product", id=product_id))


@bp_block_products.route("/products/<int:product_id>/unblock", methods=["POST"])
@login_required
@roles_required("moderator", "admin")   # ✅ només moderadors/admin poden desbloquejar
def unblock_product(product_id):
    """
    Desbloqueja un producte:
    - Comprova que el producte existeix.
    - No permet desbloquejar si no està bloquejat.
    - Elimina el registre de blocked_products.
    - Retorna al read del producte amb missatge flash.
    """
    product = Product.query.get_or_404(product_id)

    # Comprovem si està bloquejat
    if not product.blocked:
        flash("El producte no està bloquejat.", "warning")
        return redirect(url_for("products.read_product", id=product_id))

    # Esborrem el registre de bloqueig
    db.session.delete(product.blocked)
    db.session.commit()

    flash("Producte desbloquejat correctament.", "success")
    return redirect(url_for("products.read_product", id=product_id))
