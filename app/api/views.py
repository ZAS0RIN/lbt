# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, g, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from . import api
from ..decorators import check_confirmed
from ..models import User, Event
from app import db, app, NEWS_API
from ..email import send_email
from datetime import datetime, timedelta


@api.route('/get_news')
def get_news():
    for i in Event.query.filter_by(is_archive=False).order_by(Event.date.desc()).all():
        print datetime.utcnow().isoformat() > i.date.isoformat()
        print (datetime.utcnow() + timedelta(minutes=10)).isoformat() < i.date.isoformat()
        if not datetime.utcnow().isoformat() > i.date.isoformat() and not (
                    datetime.utcnow() + timedelta(minutes=10)).isoformat() < i.date.isoformat():
            return jsonify({
                'time': i.date.strftime("%Y-%m-%d %H:%M:%S"),
                'title': 'Скоро начнется матч',
                'desc': 'Играют' + i.get_name_event() + ', успевайте сделать ставки!',
                'data': True
            })
    return jsonify({
        'data': False
    })