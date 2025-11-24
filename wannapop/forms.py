from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length


# Formulari per a usuaris
class UserForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasenya", validators=[DataRequired()])
    avatar = FileField("Avatar")  # imatge pujada
    role_id = SelectField("Rol", coerce=int)   # 👈 nou camp per seleccionar rol
    submit = SubmitField("Guardar")


# Formulari per a productes
class ProductForm(FlaskForm):
    title = StringField("Títol", validators=[DataRequired()])
    description = TextAreaField("Descripció", validators=[DataRequired()])
    price = DecimalField("Preu", validators=[DataRequired()])
    photo = FileField("Foto")  # imatge pujada
    category_id = SelectField("Categoria", coerce=int)  # 👈 nou camp per seleccionar categoria
    submit = SubmitField("Guardar")


# Formulari de Login
class LoginForm(FlaskForm):
    email = StringField("Correu electrònic", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasenya", validators=[DataRequired()])
    submit = SubmitField("Iniciar sessió")


# Formulari de Registre
class RegisterForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Correu electrònic", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasenya", validators=[DataRequired(), Length(min=6)])
    avatar = FileField("Avatar (opcional)")
    submit = SubmitField("Registrar-se")
