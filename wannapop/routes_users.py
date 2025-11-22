from flask import Blueprint, render_template, abort
import logging
from wannapop.models import User

bp = Blueprint("users", __name__, url_prefix="/users")
logger = logging.getLogger(__name__)

# Ruta: /users/list
@bp.route("/list")
def list_users():
    # Consulta todos los usuarios de la BD
    users = User.query.all()
    logger.debug(f"Se han recuperado {len(users)} usuarios de la BD")
    return render_template("users/list_users.html", users=users)

# Ruta: /users/read/<id>
@bp.route("/read/<int:user_id>")
def read_user(user_id):
    # Busca un usuario por su ID
    user = User.query.get(user_id)
    if user is None:
        logger.warning(f"Usuario con id {user_id} no encontrado")
        abort(404)  # Devuelve error 404 si no existe
    return render_template("users/read_users.html", user=user)
