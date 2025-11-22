from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, Length

# ⚠️ Comentaris en català per l'exercici

# Formulari per a usuaris
class UserForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasenya", validators=[DataRequired()])
    avatar = FileField("Avatar")  # imatge pujada
    submit = SubmitField("Guardar")

# Formulari per a productes
class ProductForm(FlaskForm):
    title = StringField("Títol", validators=[DataRequired()])
    description = TextAreaField("Descripció", validators=[DataRequired()])
    price = DecimalField("Preu", validators=[DataRequired()])
    photo = FileField("Foto")  # imatge pujada
    submit = SubmitField("Guardar")
