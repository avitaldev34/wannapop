from flask import Blueprint, render_template
import logging

bp = Blueprint('users', __name__, url_prefix="/users")

logger = logging.getLogger(__name__)

@bp.route("/")
def list_users():
    users = ["Juan", "Maria", "Carlos"]
    return render_template("users/list_users.html", users=users)

@bp.route("/<int:user_id>")
def read_user(user_id):
    user = {"id": user_id, "name": f"Usuario {user_id}"}
    return render_template("users/read_users.html", user=user)
