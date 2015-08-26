# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, g
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from ..decorators import check_confirmed
from ..models import User
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from app import db
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            user = User.query.filter_by(username=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('events'))
        flash('Не правильное имя пользователя(email) или пароль')
    return render_template('login.html', form=form)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_pass():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       '/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
            return redirect(request.args.get('next') or url_for('events'))
        flash('Не правильный email')
    return render_template('reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('index'))
        if user.reset_password(token, form.password.data):
            flash('Ваш пароль был изменен.')
            return redirect(url_for('auth.login'))
            db.session.commit()
        else:
            return redirect(url_for('index'))

    return render_template('reset_password2.html', form=form)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('events'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', '/email/cnf', token=token)
        flash('Письмо с подтверждением было высланно на указанный вами email.')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.events'))
    if current_user.confirm(token):
        flash('Спасибо за регистрацию!')
    else:
        flash('Не правильный ключ активации.')
    return redirect('/events')


@auth.route('/unconfirmed')
def unconfirmed():
    print 'unc'
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect('main.events')
    return render_template('unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', '/email/cnf', token=token)
    flash('Письмо с подтверждением высланно повторно.')
    return redirect('/events')