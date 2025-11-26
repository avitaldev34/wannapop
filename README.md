# Wannapop

Aplicació web de compra-venda de productes amb gestió de rols i permisos.  
Projecte desenvolupat amb **Flask**, **SQLAlchemy**, **Flask-Login** i **Flask-WTF**.

---

## 🚀 Funcionalitats

- **Autenticació i registre d’usuaris** (login/logout).
- **Gestió de rols**:
  - `wanner`: pot crear productes.
  - `moderator`: pot bloquejar/desbloquejar usuaris i productes.
  - `admin`: pot crear/editar/eliminar usuaris i productes.
- **CRUD complet** per a usuaris i productes.
- **Bloqueig d’usuaris i productes** amb registre de moderador, raó i data.
- **Interfície amb Bootstrap-like CSS** i estils personalitzats.
- **Missatges flash** per avisos, errors i èxits.

---


---

## ⚙️ Instal·lació

1. **Clonar el repositori**:
   ```bash
   git clone <URL-del-repo>
   cd wannapop

2. **Crear entorn virtual**
    python -m venv .venv
    source .venv/bin/activate   # Linux/Mac
    .venv\Scripts\activate      # Windows

3. **instal·lar dependencies**
    pip install -r requirements.txt

4. **Initzilitzar bd.**
    flask db init
    flask db migrate
    flask db upgrade

5. **Execució**
    flask run

6. **Rols i permisos**
Wanner:

Crear productes.

Veure usuaris wanner no bloquejats.

Moderator:

Bloquejar/desbloquejar usuaris wanner.

Bloquejar/desbloquejar productes.

Admin:

Crear/editar/eliminar usuaris.

Veure tots els usuaris.

Editar/eliminar productes.

