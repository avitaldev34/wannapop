from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import os

from flask_login import login_required, current_user
from wannapop.extensions import db
from wannapop.models import Product, Category
from wannapop.forms import ProductForm

# Importem permisos de helper_role
from wannapop.helper_role import perm_read_products, perm_write_products

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
    Accessible per admin, moderator i wanner.
    - Els wanner NO veuen productes bloquejats.
    - Moderator i admin veuen tots els productes.
    """
    if not perm_read_products.can():
        flash("No tens permisos per veure productes.", "danger")
        return redirect(url_for("main.index"))

    role = current_user.role.name
    if role == "wanner":
        products = Product.query.filter(Product.blocked == None).all()
    else:
        products = Product.query.all()

    return render_template("products/list_products.html", products=products)


@bp_products.route("/products/<int:id>")
@login_required
def read_product(id):
    """
    Mostra el detall d'un producte amb la seva categoria i venedor.
    Accessible per admin, moderator i wanner.
    - Els wanner només poden veure els seus propis productes bloquejats.
    - Moderator i admin poden veure qualsevol producte.
    """
    if not perm_read_products.can():
        flash("No tens permisos per veure productes.", "danger")
        return redirect(url_for("main.index"))

    product = Product.query.get_or_404(id)

    if current_user.role.name == "wanner" and product.blocked and product.seller_id != current_user.id:
        flash("Aquest producte està bloquejat i no el pots veure.", "warning")
        return redirect(url_for("products.list_products"))

    return render_template("products/read_product.html", product=product)


@bp_products.route("/products/create", methods=["GET", "POST"])
@login_required
def create_product():
    """
    Crea un nou producte amb categoria seleccionable.
    Només wanner.
    """
    if not perm_write_products.can():
        flash("Només els usuaris amb rol 'wanner' poden crear productes.", "danger")
        return redirect(url_for("products.list_products"))

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
            seller_id=current_user.id   # venedor = usuari autenticat
        )
        db.session.add(product)
        db.session.commit()
        flash("Producte creat correctament!", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/create.html", form=form)


@bp_products.route("/products/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_product(id):
    """
    Actualitza un producte existent.
    Només el propietari (wanner).
    """
    product = Product.query.get_or_404(id)

    if product.seller_id != current_user.id or not perm_write_products.can():
        flash("Només el propietari pot modificar aquest producte.", "danger")
        return redirect(url_for("products.read_product", id=id))

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
        flash("Producte actualitzat correctament!", "success")
        return redirect(url_for("products.read_product", id=product.id))

    return render_template("products/update.html", form=form, product=product)


@bp_products.route("/products/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_product(id):
    """
    Elimina un producte i el seu bloqueig si existeix.
    Només el propietari (wanner).
    """
    product = Product.query.get_or_404(id)

    if product.seller_id != current_user.id or not perm_write_products.can():
        flash("Només el propietari pot eliminar aquest producte.", "danger")
        return redirect(url_for("products.read_product", id=id))

    if request.method == "POST":
        db.session.delete(product)
        db.session.commit()
        flash(f"Producte '{product.title}' eliminat correctament!", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/delete.html", product=product)
