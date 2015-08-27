# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from jinja2 import Markup



class LoginForm(Form):
    email = StringField('Имя пользователя или email', validators=[Required()])
    password = PasswordField('Пароль', validators=[Required()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class AddTeamForm(Form):
    name = StringField('Name')
    long_name = PasswordField('name2', validators=[Required()])
    # img aka avatar
    submit = SubmitField('Push')

class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),Email()])
    username = StringField('Имя пользователя', validators=[
    Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Имя пользователя должно начинатся с буквы, и должно содержать буквы, цифры, точку или нижнее подчеркивание')])
    password = PasswordField('Пароль', validators=[Required(), EqualTo('password2', message='Пароли должны совпадать')])
    password2 = PasswordField('Повторите пароль', validators=[Required()])
    accept = BooleanField(Markup(u"<a href='/rules'> C правилами ознакомлен</a>"), [Required()])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Данный email уже зарегистрирован')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Данное имя пользователя уже существует')


class ChangePasswordForm(Form):
    old_password = PasswordField('Старый пароль', validators=[Required()])
    password = PasswordField('Новый пароль', validators=[
        Required(), EqualTo('password2', message='Пароли должны совпадать')])
    password2 = PasswordField('Подтверждение пароля', validators=[Required()])
    submit = SubmitField('Обновить')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Сбросить пароль')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Новый пароль', validators=[
        Required(), EqualTo('password2', message='Пароли должны совпадать')])
    password2 = PasswordField('Подтверждение пароля', validators=[Required()])
    submit = SubmitField('Сбросить пароль')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Данного email нет в базе.')
