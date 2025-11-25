from flask_login import UserMixin
from datetime import datetime
from wannapop.extensions import db

# ------------------------------
# Taula Roles
# ------------------------------
class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relació amb usuaris
    users = db.relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role id={self.id} name={self.name}>"


# ------------------------------
# Taula Users
# ------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(200), nullable=False, default="user_default.jpg")

    # Clau forana cap a roles
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", back_populates="users")

    # Relació amb productes (com a venedor)
    products = db.relationship("Product", back_populates="seller", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} name={self.name} email={self.email} role_id={self.role_id}>"


# ------------------------------
# Taula Categories
# ------------------------------
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relació amb productes
    products = db.relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category id={self.id} name={self.name}>"


# ------------------------------
# Taula Products
# ------------------------------
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    photo = db.Column(db.String(255), nullable=False, default="product_default.png")

    # Clau forana cap a categories
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Category", back_populates="products")

    # Clau forana cap a users (venedor)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller = db.relationship("User", back_populates="products")

    def __repr__(self):
        return f"<Product id={self.id} title={self.title} price={self.price} category_id={self.category_id} seller_id={self.seller_id}>"


# ------------------------------
# Taula BlockedProducts
# ------------------------------
class BlockedProduct(db.Model):
    """
    Model de moderació per a productes bloquejats.
    - Cada producte pot tenir com a màxim un registre de bloqueig (clau primària = product_id).
    - Guarda qui és el moderador (usuari) i la raó del bloqueig.
    - 'created' es posa automàticament a la creació del registre.
    """
    __tablename__ = "blocked_products"

    # product_id és clau primària (no autoincrement) i també clau forana cap a products.id
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)

    # moderator_id és clau forana cap a users.id
    moderator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # reason és text obligatori amb la raó del bloqueig
    reason = db.Column(db.Text, nullable=False)

    # created guarda la data/hora de creació automàticament
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relacions
    product = db.relationship("Product", backref=db.backref("blocked", uselist=False, cascade="all, delete"))
    moderator = db.relationship("User", backref=db.backref("moderations", lazy="dynamic"))

    def __repr__(self):
        return f"<BlockedProduct product_id={self.product_id} moderator_id={self.moderator_id}>"
