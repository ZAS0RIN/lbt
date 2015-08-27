# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, TextField
from wtforms.validators import Required, Length, Email


class SetBetForm(Form):
    value1 = IntegerField('')
    submit1 = SubmitField('Oк')


class SetBetForm2(Form):
    value2 = IntegerField('')
    submit2 = SubmitField('Oк')


class EnterPromoForm(Form):
    text = StringField('Введите промокод')
    submit = SubmitField('Ок')


class QuestionsForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    text = TextField('Cообщение', validators=[Required()])
    submit1 = SubmitField('Отправить')
