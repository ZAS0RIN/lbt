from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, FloatField, DateTimeField


class AddTeamForm(Form):
    name = StringField('Name')
    long_name = StringField('name2')
    # img aka avatar
    submit = SubmitField('Push')


class AddEventForm(Form):
    team1_id = IntegerField('Team ID')
    team1_k = FloatField('Team 1 K')
    team12_k = FloatField('1=2')
    team2_k = FloatField('Team 2 K')
    team2_id = IntegerField('Team ID')
    date = DateTimeField('Date Actions')
    submit = SubmitField('Push')


class ResultForm(Form):
    res = IntegerField('Team ID')
    submit = SubmitField('Push')


class EditEventForm(Form):
    team1_k = FloatField('Team 1 K')
    team2_k = FloatField('Team 2 K')

    submit = SubmitField('Push')
