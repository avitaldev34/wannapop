from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

# ------------------------------
# Formulari per a usuaris (CRUD)
# ------------------------------
class UserForm(FlaskForm):
    # Nom obligatori, mínim 2 caràcters i màxim 50
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    # Correu electrònic obligatori i amb format vàlid
    email = StringField("Email", validators=[DataRequired(), Email()])
    # Contrasenya obligatòria
    password = PasswordField("Contrasenya", validators=[DataRequired()])
    # Avatar opcional (fitxer pujat)
    avatar = FileField("Avatar")
    # Selecció de rol (admin, moderator, wanner) → coerce=int per guardar l'ID
    role_id = SelectField("Rol", coerce=int)
    # Botó de guardar
    submit = SubmitField("Guardar")


# ------------------------------
# Formulari per a productes (CRUD)
# ------------------------------
class ProductForm(FlaskForm):
    # Títol obligatori
    title = StringField("Títol", validators=[DataRequired()])
    # Descripció obligatòria
    description = TextAreaField("Descripció", validators=[DataRequired()])
    # Preu obligatori (DecimalField per permetre decimals)
    price = DecimalField("Preu", validators=[DataRequired()])
    # Foto opcional
    photo = FileField("Foto")
    # Categoria obligatòria (coerce=int per guardar l'ID)
    category_id = SelectField("Categoria", coerce=int, validators=[DataRequired()])
    # Botó de guardar
    submit = SubmitField("Guardar")


# ------------------------------
# Formulari de Login
# ------------------------------
class LoginForm(FlaskForm):
    # Correu electrònic obligatori i amb format vàlid
    email = StringField("Correu electrònic", validators=[DataRequired(), Email()])
    # Contrasenya obligatòria
    password = PasswordField("Contrasenya", validators=[DataRequired()])
    # Botó d'inici de sessió
    submit = SubmitField("Iniciar sessió")


# ------------------------------
# Formulari de Registre
# ------------------------------
class RegisterForm(FlaskForm):
    # Nom obligatori, mínim 2 caràcters i màxim 50
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    # Correu electrònic obligatori i amb format vàlid
    email = StringField("Email", validators=[DataRequired(), Email()])
    # Contrasenya obligatòria, mínim 4 caràcters
    password = PasswordField("Contrasenya", validators=[DataRequired(), Length(min=4)])
    # Avatar opcional
    avatar = FileField("Avatar")
    # Selecció de rol (es carrega des de la BD en la vista register)
    role = SelectField("Rol", choices=[], coerce=int)
    # Botó de registre
    submit = SubmitField("Registrar")
