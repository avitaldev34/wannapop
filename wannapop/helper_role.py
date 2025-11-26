from flask_principal import Permission, RoleNeed, Identity, identity_changed
from flask import current_app

# ------------------------------
# Definició de rols
# ------------------------------
WANNER = RoleNeed("wanner")
MODERATOR = RoleNeed("moderator")
ADMIN = RoleNeed("admin")

# ------------------------------
# Permisos per accions
# ------------------------------

# Usuaris
# Wanner, moderator i admin poden llegir usuaris
perm_read_users = Permission(WANNER, MODERATOR, ADMIN)       # llegir usuaris
perm_write_users = Permission(ADMIN)                         # crear/editar/esborrar usuaris
perm_moderate_users = Permission(MODERATOR, ADMIN)           # bloquejar/desbloquejar usuaris

# Productes
# Wanner pot llegir i escriure productes, moderator i admin també poden llegir
perm_read_products = Permission(WANNER, MODERATOR, ADMIN)    # llegir productes
perm_write_products = Permission(WANNER)                     # crear/editar/esborrar productes
perm_moderate_products = Permission(MODERATOR, ADMIN)        # bloquejar/desbloquejar productes

# ------------------------------
# Helper per establir identitat en login
# ------------------------------
def set_identity_on_login(app, user):
    """
    Assigna la identitat de Flask-Principal quan un usuari inicia sessió.
    """
    if not user or not getattr(user, "role", None):
        return

    identity = Identity(user.id)

    role_name = user.role.name
    if role_name == "wanner":
        identity.provides.add(WANNER)
    elif role_name == "moderator":
        identity.provides.add(MODERATOR)
    elif role_name == "admin":
        identity.provides.add(ADMIN)

    # Notifica a Flask-Principal que la identitat ha canviat
    identity_changed.send(app._get_current_object(), identity=identity)
