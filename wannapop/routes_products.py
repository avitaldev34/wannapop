from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import os

from flask_login import login_required, current_user
from wannapop.extensions import db
from wannapop.models import Product, Category, BlockedProduct
from wannapop.forms import ProductForm

bp_products = Blueprint("products", __name__)

UPLOAD_FOLDER = os.path.join("wannapop", "static", "uploads")
DEFAULT_PHOTO = "product_default.png"

# ------------------------------
# PRODUCTES
# ------------------------------

@bp_products.route("/products")
@login_required
def list_products():
    """
    Llista tots els productes amb la seva categoria i venedor.
    Gràcies al relationship back_populates podem accedir a product.category.name i product.seller.name.
    """
    products = Product.query.all()
    return render_template("products/list_products.html", products=products)


@bp_products.route("/products/<int:id>")
@login_required
def read_product(id):
    """
    Mostra el detall d'un producte amb la seva categoria i venedor.
    """
    product = Product.query.get_or_404(id)
    return render_template("products/read_product.html", product=product)


@bp_products.route("/products/create", methods=["GET", "POST"])
@login_required
def create_product():
    """
    Crea un nou producte amb categoria seleccionable.
    """
    form = ProductForm()
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if not categories:
        flash("Has de crear categories abans de poder crear productes.", "warning")
        return redirect(url_for("products.list_products"))

    if form.validate_on_submit():
        filename = DEFAULT_PHOTO
        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.photo.data.save(filepath)

        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            photo=filename,
            category_id=form.category_id.data,
            seller_id=current_user.id   # ✅ venedor = usuari autenticat
        )
        db.session.add(product)
        db.session.commit()
        flash("Producte creat correctament!", "success")  # ✅ missatge flash
        return redirect(url_for("products.list_products"))

    return render_template("products/create.html", form=form)


@bp_products.route("/products/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_product(id):
    """
    Actualitza un producte existent.
    """
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.category_id = form.category_id.data

        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.photo.data.save(filepath)
            product.photo = filename
        elif not product.photo:
            product.photo = DEFAULT_PHOTO

        db.session.commit()
        flash("Producte actualitzat correctament!", "success")  # ✅ missatge flash
        return redirect(url_for("products.read_product", id=product.id))

    return render_template("products/update.html", form=form, product=product)


@bp_products.route("/products/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_product(id):
    """
    Elimina un producte i el seu bloqueig si existeix.
    """
    product = Product.query.get_or_404(id)

    if request.method == "POST":
        block = BlockedProduct.query.filter_by(product_id=id).first()
        if block:
            db.session.delete(block)

        db.session.delete(product)
        db.session.commit()
        flash(f"Producte '{product.title}' eliminat correctament!", "success")  # ✅ missatge flash
        return redirect(url_for("products.list_products"))

    return render_template("products/delete.html", product=product)
