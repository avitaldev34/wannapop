from flask import Blueprint, render_template

bp = Blueprint('products', __name__, url_prefix="/products")

@bp.route("/")
def list_products():
    products = ["Producto A", "Producto B", "Producto C"]
    return render_template("products/list_products.html", products=products)

@bp.route("/<int:product_id>")
def read_product(product_id):
    product = {"id": product_id, "name": f"Producto {product_id}"}
    return render_template("products/read_products.html", product=product)
