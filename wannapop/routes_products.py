from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
import os
from werkzeug.utils import secure_filename
from wannapop.models import Product, db
from wannapop.forms import ProductForm

bp = Blueprint("products", __name__, url_prefix="/products")

# Ruta: /products/list
@bp.route("/list")
def list_products():
    products = Product.query.all()
    return render_template("products/list_products.html", products=products)

# Ruta: /products/read/<id>
@bp.route("/read/<int:product_id>")
def read_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        abort(404)
    return render_template("products/read_products.html", product=product)

# Ruta: /products/create
@bp.route("/create", methods=["GET", "POST"])
def create_product():
    form = ProductForm()
    if request.method == "POST":
        if form.validate_on_submit():
            photo_filename = None

            if form.photo.data:
                filename = secure_filename(form.photo.data.filename)
                uploads_dir = current_app.config["UPLOAD_FOLDER"]
                os.makedirs(uploads_dir, exist_ok=True)
                photo_path = os.path.join(uploads_dir, filename)
                form.photo.data.save(photo_path)
                photo_filename = filename

            # Imagen por defecto si no se sube ninguna
            if not photo_filename:
                photo_filename = "product_default.png"

            new_product = Product(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                photo=photo_filename
            )
            db.session.add(new_product)
            db.session.commit()

            flash("Producte creat correctament!", "success")
            return redirect(url_for("products.list_products"))
        else:
            flash("Errors en el formulari", "danger")

    return render_template("products/create.html", form=form)

# Ruta: /products/update/<id>
@bp.route("/update/<int:product_id>", methods=["GET", "POST"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        abort(404)

    form = ProductForm(obj=product)

    if request.method == "POST":
        if form.validate_on_submit():
            product.title = form.title.data
            product.description = form.description.data
            product.price = form.price.data

            if form.photo.data:
                filename = secure_filename(form.photo.data.filename)
                uploads_dir = current_app.config["UPLOAD_FOLDER"]
                os.makedirs(uploads_dir, exist_ok=True)
                photo_path = os.path.join(uploads_dir, filename)
                form.photo.data.save(photo_path)
                product.photo = filename

            # Imagen por defecto si no tiene ninguna
            if not product.photo:
                product.photo = "product_default.png"

            db.session.commit()
            flash("Producte actualitzat correctament!", "success")
            return redirect(url_for("products.list_products"))
        else:
            flash("Errors en el formulari", "danger")

    return render_template("products/update.html", form=form, product=product)

# Ruta: /products/delete/<id>
@bp.route("/delete/<int:product_id>", methods=["GET", "POST"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        abort(404)

    if request.method == "POST":
        db.session.delete(product)
        db.session.commit()
        flash("Producte eliminat correctament!", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/delete.html", product=product)
