# -*- coding: utf-8 -*-
from . import login_manager
from flask_login import UserMixin
from flask import flash
from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

ROLE_USER = 0
ROLE_MODERATOR = 1
ROLE_ADMIN = 2
TYPE_PROMO = 0
TYPE_BET = 1
TYPE_IN_MONEY = 2
TYPE_OUT_MONEY = 3
PROMOCODE = 'LOLBETS50'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    balance = db.Column(db.Integer, default=0)
    bets = db.relationship('Bet', backref='author', lazy='dynamic')
    confirmed = db.Column(db.Boolean, default=False)
    promo50 = db.Column(db.Boolean, default=False)
    history = db.relationship('History', backref='author', lazy='dynamic')

    def activate_promo(self, txt):
        if txt == PROMOCODE and not self.promo50:
            self.balance += 50
            self.promo50 = True
            h = History(type=TYPE_PROMO, author_id=self.id, money=50, loss=False, text='promo',
                        date=datetime.utcnow())
            db.session.add(h)
            db.session.commit()
            flash('Ваш счет пополнен на 50 рублей')
            return True
        return False

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_reset_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.commit()
        return True

    def confirm(self, token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.commit()
        return True

    def __repr__(self):
        return '<User %r>' % (self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    # id2 = db.Column(db.Integer, index=True)
    name = db.Column(db.String(64))
    long_name = db.Column(db.String(64))
    bets = db.relationship('Bet', backref='author_team', lazy='dynamic')
    #    events = db.relationship('Event', backref='author_team', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.name)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), index=True)
    team1_k = db.Column(db.Integer)
    team12_k = db.Column(db.Integer, default=None)
    team2_k = db.Column(db.Integer)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), index=True)
    date = db.Column(db.DateTime, index=True)
    bets = db.relationship('Bet', backref='author_event', lazy='dynamic')
    is_archive = db.Column(db.Boolean, default=False, index=True)
    team_win = db.Column(db.Integer, default=False, index=True)

    def get_name_event(self):
        return self.get_data()[0] + ' vs ' + self.get_data()[1]

    def get_data(self):
        t1 = Team.query.get_or_404(self.team1_id)
        if t1.long_name:
            t1 = t1.name + '(' + t1.long_name + ')'
        else:
            t1 = t1.name
        t2 = Team.query.get_or_404(self.team2_id)
        if t2.long_name:
            t2 = t2.name + '(' + t2.long_name + ')'
        else:
            t2 = t2.name
        return [t1, t2]

    def set_win_team(self, win_id):
        if win_id == self.team1_id or win_id == self.team2_id:
            if win_id == self.team1_id:
                self.team_win = self.team1_id
            else:
                self.team_win = self.team2_id
            for i in self.bets.all():
                i.result(win_id)
            self.is_archive = True
            db.session.commit()

    def del_event(self):
        for i in self.bets.all():
            i.recash()
        self.is_archive = True
        db.session.commit()

    def __repr__(self):
        return '<Event %r>' % (self.get_name_event())


class Bet(db.Model):
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), index=True)
    k = db.Column(db.Float)
    cash = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    is_archive = db.Column(db.Boolean, default=False, index=True)
    win = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    def result(self, win_id):
        if self.team_id == win_id and self.is_archive != True:
            u = User.query.get_or_404(int(self.author_id))
            u.balance = u.balance + int(self.k * self.cash + 0.5)
            self.is_archive = True
            self.win = True
            h = History(type=TYPE_BET, author_id=self.author_id, money=int(self.k * self.cash + 0.5), loss=False,
                        text='good', event_id=self.event_id, date=datetime.utcnow())
            db.session.add(h)
            db.session.commit()

        else:
            self.is_archive = True
            db.session.commit()

    def recash(self):
        if self.is_archive != True:
            u = User.query.get_or_404(int(self.author_id))
            u.balance = u.balance + self.cash
            h = History(type=TYPE_BET, author_id=self.author_id, money=self.cash, loss=False, event_id=self.event_id,
                        text='recash', date=datetime.utcnow())
            db.session.add(h)
            self.is_archive = True
            self.win = None
            db.session.commit()

    def __repr__(self):
        return '<Bet %r>' % (self.id)


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, index=True)
    # type {
    #   0 promocode
    #   1 bet
    #   2 in_money
    #   3 out_money
    #  }
    money = db.Column(db.Integer)
    loss = db.Column(db.Boolean, index=True, default=None)
    text = db.Column(db.String, default=None)
    #  bet.replace('Ставка')
    #  recash.("возврат средств")
    #  promo.
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), index=True, default=None)
    date = db.Column(db.DateTime)

    def __repr__(self):
        return '<History %r>' % (self.text)
