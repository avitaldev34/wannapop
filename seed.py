from wannapop import create_app
from wannapop.extensions import db
from wannapop.models import Product, Category, User, Role

app = create_app()

with app.app_context():
    # Asignar categoría por defecto a productos
    default_category = Category.query.filter_by(name="tecnologia").first()
    for p in Product.query.all():
        p.category_id = default_category.id

    # Asignar rol por defecto a usuarios
    default_role = Role.query.filter_by(name="wanner").first()
    for u in User.query.all():
        u.role_id = default_role.id

    db.session.commit()
    print("Datos actualizados correctamente ✅")
