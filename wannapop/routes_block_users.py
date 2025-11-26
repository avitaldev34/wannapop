from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from wannapop.extensions import db
from wannapop.models import User, BlockedUser

bp_block_users = Blueprint("block_users", __name__)

def roles_required(*roles):
    def wrapper(fn):
        from functools import wraps
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Has d'iniciar sessió per accedir.", "danger")
                return redirect(url_for("auth.login"))
            if current_user.role.name not in roles:
                flash("No tens permisos per fer aquesta acció.", "danger")
                return redirect(url_for("users.read_user", id=kwargs.get("user_id")))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@bp_block_users.route("/users/<int:user_id>/block", methods=["POST"])
@login_required
@roles_required("moderator", "admin")
def block_user(user_id):
    user = User.query.get_or_404(user_id)

    # Només es poden bloquejar usuaris wanner
    if user.role.name != "wanner":
        flash("Només es poden bloquejar usuaris amb rol 'wanner'.", "warning")
        return redirect(url_for("users.read_user", id=user_id))

    # Evitar que un admin es bloquegi a si mateix
    if user.id == current_user.id:
        flash("No pots bloquejar-te a tu mateix.", "danger")
        return redirect(url_for("users.read_user", id=user_id))

    if user.blocked:
        flash("L'usuari ja està bloquejat.", "warning")
        return redirect(url_for("users.read_user", id=user_id))

    reason = request.form.get("reason", "").strip()
    if not reason:
        flash("Has d'indicar una raó per bloquejar l'usuari.", "danger")
        return redirect(url_for("users.read_user", id=user_id))

    bloqueig = BlockedUser(user_id=user.id, moderator_id=current_user.id, reason=reason)
    db.session.add(bloqueig)
    db.session.commit()

    flash("Usuari bloquejat correctament.", "success")
    return redirect(url_for("users.read_user", id=user_id))


@bp_block_users.route("/users/<int:user_id>/unblock", methods=["POST"])
@login_required
@roles_required("moderator", "admin")
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)

    if not user.blocked:
        flash("L'usuari no està bloquejat.", "warning")
        return redirect(url_for("users.read_user", id=user_id))

    db.session.delete(user.blocked)
    db.session.commit()

    flash("Usuari desbloquejat correctament.", "success")
    return redirect(url_for("users.read_user", id=user_id))
