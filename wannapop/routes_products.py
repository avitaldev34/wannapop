from flask import Blueprint, render_template
from wannapop.models import Product

bp = Blueprint('products', __name__, url_prefix="/products")

@bp.route("/list")
def list_products():
    products = Product.query.all()
    products = ["Producto A", "Producto B", "Producto C"]
    return render_template("products/list_products.html", products=products)

@bp.route("/read<int:product_id>")
def read_product(product_id):
    product = {"id": product_id, "name": f"Producto {product_id}"}
    return render_template("products/read_products.html", product=product)
