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

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", back_populates="users")

    products = db.relationship("Product", back_populates="seller", cascade="all, delete-orphan")

    # relació amb bloqueig d'usuari (1:1)
    blocked = db.relationship(
        "BlockedUser",
        foreign_keys="BlockedUser.user_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User id={self.id} name={self.name} email={self.email} role_id={self.role_id}>"


# ------------------------------
# Taula Categories
# ------------------------------
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

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

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Category", back_populates="products")

    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller = db.relationship("User", back_populates="products")

    def __repr__(self):
        return f"<Product id={self.id} title={self.title} price={self.price} category_id={self.category_id} seller_id={self.seller_id}>"


# ------------------------------
# Taula BlockedProducts
# ------------------------------
class BlockedProduct(db.Model):
    __tablename__ = "blocked_products"

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)
    moderator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("blocked", uselist=False, cascade="all, delete"))
    moderator = db.relationship("User", backref=db.backref("moderations_products", lazy="dynamic"))

    def __repr__(self):
        return f"<BlockedProduct product_id={self.product_id} moderator_id={self.moderator_id}>"


# ------------------------------
# Taula BlockedUsers
# ------------------------------
class BlockedUser(db.Model):
    __tablename__ = "blocked_users"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    moderator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="blocked"
    )
    moderator = db.relationship(
        "User",
        foreign_keys=[moderator_id],
        backref=db.backref("moderations_users", lazy="dynamic")
    )

    def __repr__(self):
        return f"<BlockedUser user_id={self.user_id} moderator_id={self.moderator_id}>"
