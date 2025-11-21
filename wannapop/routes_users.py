from flask import Blueprint, render_template
from .models import User

users = Blueprint("users", __name__, url_prefix="/users")

@users.route("/list")
def list_users():
    users = User.query.all()
    return render_template("users/list_users.html", users=users)
