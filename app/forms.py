# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import SubmitField, IntegerField, StringField


class SetBetForm(Form):
    value1 = IntegerField('')
    submit1 = SubmitField('Oк')


class SetBetForm2(Form):
    value2 = IntegerField('')
    submit2 = SubmitField('Oк')


class EnterPromoForm(Form):
    text = StringField('Введите промокод')
    submit = SubmitField('Ок')
