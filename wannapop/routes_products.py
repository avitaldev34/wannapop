from flask import Blueprint, render_template
from .models import Product

products = Blueprint("products", __name__, url_prefix="/products")

@products.route("/list")
def list_products():
    products = Product.query.all()
    return render_template("products/list_products.html", products=products)
