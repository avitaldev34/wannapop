from flask import Blueprint, render_template, redirect, url_for, flash, request
from wannapop.extensions import db
from wannapop.models import Product, Category, User, Role
from wannapop.forms import ProductForm, UserForm

bp = Blueprint("main", __name__)

# ------------------------------
# Ruta principal "/"
# ------------------------------
@bp.route("/")
def index():
    return render_template("index.html")

# ------------------------------
# Ruta de prueba "/hello"
# ------------------------------
@bp.route("/hello")
def hello():
    return "<h1>Hello, Wannapop!</h1>"

# ------------------------------
# PRODUCTES
# ------------------------------
@bp.route("/products")
def list_products():
    products = Product.query.all()
    return render_template("products/list_products.html", products=products)

@bp.route("/products/<int:id>")
def read_product(id):
    product = Product.query.get_or_404(id)
    return render_template("products/read_product.html", product=product)

@bp.route("/products/create", methods=["GET", "POST"])
def create_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            photo=form.photo.data.filename if form.photo.data else None,
            category_id=form.category_id.data,
            seller_id=1  # de momento asignamos un vendedor fijo (ej. id=1)
        )
        db.session.add(product)
        db.session.commit()
        flash("Producte creat correctament!", "success")
        return redirect(url_for("main.list_products"))
    return render_template("products/create.html", form=form)

@bp.route("/products/update/<int:id>", methods=["GET", "POST"])
def update_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        flash("Producte actualitzat correctament!", "success")
        return redirect(url_for("main.read_product", id=product.id))
    return render_template("products/update.html", form=form, product=product)

@bp.route("/products/delete/<int:id>", methods=["GET", "POST"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(product)
        db.session.commit()
        flash(f"Producte '{product.title}' eliminat correctament!", "success")
        return redirect(url_for("main.list_products"))
    return render_template("products/delete.html", product=product)

# ------------------------------
# USERS
# ------------------------------
@bp.route("/users")
def list_users():
    users = User.query.all()
    return render_template("users/list_users.html", users=users)

@bp.route("/users/<int:id>")
def read_user(id):
    user = User.query.get_or_404(id)
    return render_template("users/read_user.html", user=user)

@bp.route("/users/create", methods=["GET", "POST"])
def create_user():
    form = UserForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            avatar=form.avatar.data.filename if form.avatar.data else None,
            role_id=form.role_id.data
        )
        db.session.add(user)
        db.session.commit()
        flash("Usuari creat correctament!", "success")
        return redirect(url_for("main.list_users"))
    return render_template("users/create.html", form=form)

@bp.route("/users/update/<int:id>", methods=["GET", "POST"])
def update_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash("Usuari actualitzat correctament!", "success")
        return redirect(url_for("main.read_user", id=user.id))
    return render_template("users/update.html", form=form, user=user)

@bp.route("/users/delete/<int:id>", methods=["GET", "POST"])
def delete_user(id):
    user = User.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        flash(f"Usuari '{user.name}' eliminat correctament!", "success")
        return redirect(url_for("main.list_users"))
    return render_template("users/delete.html", user=user)
