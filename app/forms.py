from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField('Repita a senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor, use um nome de usuário diferente.')

class BookForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    author = StringField('Autor', validators=[DataRequired()])
    genero = StringField('Gênero', validators=[DataRequired()])
    available = BooleanField('Disponível')
    submit = SubmitField('Salvar')

class PersonForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Salvar')

class BorrowForm(FlaskForm):
    book_id = SelectField('Livro', coerce=int, validators=[DataRequired()])
    person_id = SelectField('Pessoa', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Emprestar')
