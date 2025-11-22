# Wannapop — Projecte de compra i venda de productes de segona mà

Aquest projecte és una aplicació web desenvolupada amb Flask que permet la compra i venda de productes de segona mà. A continuació es detallen els passos seguits fins a la versió actual.

---

## Estructura del projecte

2526-projecte-1-equip/ ├── .venv/ # Entorn virtual (ignorat) ├── instance/ │ └── sqlite/ │ ├── database.db # Base de dades local (ignorada) │ ├── database.db.initial # Base de dades inicial │ └── init.sql # Script SQL per crear la BD ├── static/ # Fitxers estàtics ├── templates/ # Plantilles HTML ├── wappazon/ # Codi font de l'aplicació Flask │ ├── init.py │ ├── config.py │ ├── models.py │ ├── routes_users.py │ └── routes_products.py └── README.md # Aquest document


---

## Configuració

- El projecte utilitza **Flask** com a framework web.
- La base de dades és **SQLite**, ubicada a `instance/sqlite/database.db`.
- La configuració es troba a `wappazon/config.py`.

---

## Base de dades

La base de dades no es puja al repositori (`database.db` està al `.gitignore`).

Cada membre de l’equip ha de crear la seva pròpia còpia a partir de l’script `init.sql` o bé copiar la base inicial:

### Opció 1: Crear des de l’script
```bash
sqlite3 instance/sqlite/database.db < instance/sqlite/init.sql




