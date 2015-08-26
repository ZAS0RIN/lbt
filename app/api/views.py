# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, g, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from . import api
from ..decorators import check_confirmed
from ..models import User
from app import db
from ..email import send_email

@api.route('/get_news')
def get_news():
    pass


