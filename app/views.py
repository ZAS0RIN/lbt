# -*- coding: utf-8 -*-
from app import app, db
from flask import Flask, render_template, flash, redirect, url_for, request, g

from models import Event, Bet, Team, User, History, TYPE_BET
from forms import SetBetForm, SetBetForm2, EnterPromoForm, QuestionsForm
from auth.forms import ChangePasswordForm
from decorators import check_confirmed
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user


@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/events')
def events():
    events = Event.query.filter_by(is_archive=False).order_by(Event.date.desc()).all()
    events.reverse()
    return render_template('index.html', events=events, title_name='События')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        print 'f1'
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.commit()
            flash('Ваш пароль был изменен.')
            return redirect(url_for('events'))
        else:
            flash('Не верный пароль.')
    return render_template('profile.html', form=form)


@app.route('/balance', methods=['GET', 'POST'])
@login_required
@check_confirmed
def balance():
    EPF = EnterPromoForm()
    if EPF.validate_on_submit():
        if current_user.activate_promo(EPF.text.data):
            flash('Код принят')
            return redirect('/events')
        else:
            flash('Не верный код или он был уже активирован')
    h = History.query.filter_by(author_id=current_user.id).all()
    h.reverse()
    return render_template('balance.html', history=h, form=EPF)
    # return render_template('balance.html', form=EPF)


@app.route('/mybets')
@login_required
def mybets():
    active = current_user.bets.filter_by(is_archive=False).all()
    active.reverse()
    passive = current_user.bets.filter_by(is_archive=True).all()
    passive.reverse()
    return render_template('mybets.html', active=active, passive=passive)


@app.route('/event/all/')
def event_all():
    e = Event.query.all()
    return render_template('event.html', events=e, title_name='Все события')


@app.route('/event/<int:id>/', methods=['GET', 'POST'])
@login_required
@check_confirmed
def event_id(id):
    e = Event.query.filter_by(id=id).first()
    form1 = SetBetForm()
    form2 = SetBetForm2()

    g.minbet = app.config['MINIMUM_BET']
    if e.is_archive or datetime.utcnow().isoformat() > e.date.isoformat():
        form1 = None
        form2 = None
        flash('Событие началось')
    else:
        if form1.validate_on_submit() and form1.value1.data != None:
            if int(form1.value1.data) < app.config['MINIMUM_BET']:
                flash('Минимальная ставка 50')
                return redirect('/events')
            if e.is_archive:
                flash('Событие уже прошло')
                return redirect('/events')
            if form1.value1.data > current_user.balance:
                flash('Не достаточно средств')
                return redirect('/events')
            b = Bet(team_id=e.team1_id, event_id=id, k=e.team1_k, cash=form1.value1.data, author_id=current_user.id,
                    date=datetime.utcnow())
            h = History(type=TYPE_BET, money=-form1.value1.data, loss=True, text='bet', author_id=current_user.id,
                        event_id=id, date=datetime.utcnow())
            db.session.add(h)
            db.session.add(b)
            User.query.filter_by(id=current_user.id).first().balance -= form1.value1.data
            db.session.commit()
            flash('Ставка принята')
            return redirect(url_for('events'))

        if form2.validate_on_submit() and form2.value2.data != None:
            if form2.value2.data < app.config['MINIMUM_BET']:
                flash('Минимальная ставка 50')
                return redirect('/events')
            if e.is_archive:
                flash('Событие уже прошло')
                return redirect('/events')
            if form2.value2.data > current_user.balance:
                flash('Не достаточно средств')
                return redirect('/events')
            b = Bet(team_id=e.team2_id, event_id=id, k=e.team2_k, cash=form2.value2.data, author_id=current_user.id,
                    date=datetime.utcnow())
            h = History(type=TYPE_BET, money=-form2.value2.data, loss=True, text='bet', author_id=current_user.id,
                        event_id=id, date=datetime.utcnow())
            db.session.add(h)
            db.session.add(b)
            User.query.filter_by(id=current_user.id).first().balance -= form2.value2.data
            db.session.commit()
            flash('Ставка принята')
            return redirect(url_for('events'))
    team1_history = Event.query.filter_by(team1_id=e.team1_id).filter_by(is_archive=True).union(
        Event.query.filter_by(team2_id=e.team1_id).filter_by(is_archive=True)).order_by(Event.date.desc()).all()
    team1_history.reverse()
    team2_history = Event.query.filter_by(team1_id=e.team2_id).filter_by(is_archive=True).union(
        Event.query.filter_by(team2_id=e.team2_id).filter_by(is_archive=True)).order_by(Event.date.desc()).all()
    team2_history.reverse()
    try:
        team1_history.remove(e)
        team2_history.remove(e)
    except:
        pass
    return render_template('event.html', events=[e], title_name=e.get_data()[0] + ' - ' + e.get_data()[1],
                           t1h=team1_history, t2h=team2_history, t1name=e.get_data()[0], t2name=e.get_data()[1],
                           form1=form1, form2=form2)


@app.route('/rules')
def rules():
    return render_template('rules.html')


@app.route('/about', methods=['POST','GET'])
def about():
    form = QuestionsForm()
    if form.validate_on_submit():
        flash('Сообщение отправленно')
        return redirect('/events')
    return render_template('about.html', form=form)


@app.route('/result_cash/<data>', methods=['POST', 'GET'])
def parse_result(data):
    request.url
    return render_template('404.html')



@app.route('/3058fc2ea731.html', methods=['POST','GET'])
def yandex():
    return render_template('3058fc2ea731.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
