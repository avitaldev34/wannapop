from flask import Blueprint, render_template, abort
from wannapop.models import Product

bp = Blueprint("products", __name__, url_prefix="/products")

# Ruta: /products/list
@bp.route("/list")
def list_products():
    # Consulta todos los productos de la BD
    products = Product.query.all()
    return render_template("products/list_products.html", products=products)

# Ruta: /products/read/<id>
@bp.route("/read/<int:product_id>")
def read_product(product_id):
    # Busca un producto por su ID
    product = Product.query.get(product_id)
    if product is None:
        abort(404)  # Devuelve error 404 si no existe
    return render_template("products/read_products.html", product=product)
