from flask_login import login_required

from . import admin
from ..models import Team, User, Event
from .forms import AddTeamForm, AddEventForm, ResultForm, EditEventForm


# from ..parser import parseWTV2


@admin.route('/set_win')
@login_required
def set_win():
    if current_user.role < 1:
        return render_template('404.html'), 404
    e = Event.query.filter_by(is_archive=False).order_by(Event.date.desc()).all()
    e.reverse()
    return render_template('admin/set_win.html', events=e)


@admin.route('/set_win/<int:id>/<int:idteam>')
@login_required
def set_win_id(id, idteam):
    if current_user.role < 1:
        return render_template('404.html'), 404
    e = Event.query.filter_by(id=id).first()
    e.set_win_team(idteam)
    flash('gj')
    return render_template('admin/index.html')


@admin.route('/add_event', methods=['GET', 'POST'])
@login_required
def addevent():
    if current_user.role != 2:
        return render_template('404.html'), 404
    form = AddEventForm()
    if form.validate_on_submit():
        e = Event(team1_id=form.team1_id.data, team2_id=form.team2_id.data, team1_k=form.team1_k.data,
                  team2_k=form.team2_k.data, date=form.date.data)
        db.session.add(e)
        db.session.commit()
        flash('Add event - OK.')
        return redirect(request.args.get('next') or url_for('index'))
    teams = Team.query.all()
    return render_template('admin/addevent.html', form=form, teams=teams,
                           events=Event.query.filter_by(is_archive=False).all(), time=datetime.utcnow())


@admin.route('/all_team')
@login_required
def allteam():
    if current_user.role != 2:
        return render_template('404.html'), 404
    teams = Team.query.all()
    return render_template('admin/allteam.html', teams=teams)


@admin.route('/events')
@login_required
def event_all():
    if current_user.role < 1:
        return render_template('404.html'), 404
    return render_template('admin/events.html', events=Event.query.filter_by(is_archive=False).all())


# @admin.route('/event/<int:id>', methods=['GET', 'POST'])
# @login_required
def event_id(id):
    if current_user.role < 1:
        return render_template('404.html'), 404
    try:
        e = Event.query.get_or_404(id)
    except:
        return render_template('404.html'), 404
    form = ResultForm()
    if form.validate_on_submit():
        e.set_win_team(form.res.data)

    return render_template('admin/events.html', event=e, form=form)


@admin.route('/all_users')
@login_required
def allusers():
    if current_user.role != 2:
        return render_template('404.html'), 404
    users = User.query.all()
    return render_template('admin/allusers.html', users=users)


@admin.route('/parseWTV')
@login_required
def parseWTV():
    parseWTV2()
    return redirect(url_for('events'))


@admin.route('/add_team/<name>/<longname>', methods=['GET', 'POST'])
@login_required
def addteam_data(name, longname=''):
    if current_user.role != 2:
        return render_template('404.html'), 404
    if not Team.query.filter_by(name=name).first():
        t = Team(name=name, long_name=longname)
        db.session.add(t)
        db.session.commit()
        flash('Add team - OK.')
    return redirect(request.args.get('next') or url_for('index'))


@admin.route('/add_team/', methods=['GET', 'POST'])
@login_required
def addteam():
    if current_user.role != 2:
        return render_template('404.html'), 404
    form = AddTeamForm()
    if form.validate_on_submit():
        t = Team(name=form.name.data, long_name=form.long_name.data)
        db.session.add(t)
        db.session.commit()
        flash('Add team - OK.')
        return redirect(url_for('admin.index'))
    return render_template('/admin/addteam.html', form=form)


@admin.route('/team/<int:id>', methods=['GET', 'POST'])
@login_required
# gh4p1n2s1d
def edit_team(id):
    t = Team.query.filter_by(id=id).first()
    if current_user.role != 2 and not t:
        return render_template('404.html'), 404
    form = AddTeamForm()
    if form.validate_on_submit():
        if form.name.data:
            t.name = form.name.data
        if form.long_name.data:
            t.long_name = form.long_name.data
        db.session.commit()
        flash('Change - OK')
        return redirect(url_for('admin.index'))
    return render_template('admin/addteam.html', form=form, team=t)


@admin.route('/event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    e = Event.query.filter_by(id=id).first()
    if current_user.role != 2 and not e:
        return render_template('404.html'), 404
    form = EditEventForm()
    if not form.team1_k.data:
        form.team1_k.data = e.team1_k
    if not form.team2_k.data:
        form.team2_k.data = e.team2_k
    if form.validate_on_submit():
        if form.team1_k.data:
            e.team1_k = form.team1_k.data
        if form.team2_k.data:
            e.team2_k = form.team2_k.data
        db.session.commit()
        flash('Change - OK')
        return redirect(url_for('admin.index'))
    return render_template('admin/events.html', form=form, events=[e])


@admin.route('/event/del/<int:id>', methods=['GET', 'POST'])
@login_required
def del_event(id):
    e = Event.query.filter_by(id=id).first()
    if current_user.role != 2 and not e:
        return render_template('404.html'), 404
    e.del_event()
    flash('del - OK')
    return redirect(url_for('admin.index'))


# @admin.route('/user/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_user(id):
#    u = Team.query.filter_by(id=id).first()
#    if current_user.role != 2 and not u:
#        return render_template('404.html'), 404
#    form = AddTeamForm()
#    if form.validate_on_submit():
#        if form.name.data:
#            u.name = form.name.data
#        if form.long_name.data:
#            u.long_name = form.long_name.data
#        db.session.commit()
#        flash('Change - OK')
#       return redirect(url_for('admin.index'))
#    return render_template('admin/addteam.html', form=form, user=u)




@admin.route('/')
@admin.route('/index')
@login_required
def index():
    need = []
    if current_user.role < 1:
        return render_template('404.html'), 404
    for i in Event.query.filter_by(is_archive=False).all():
        if i.date.isoformat() < datetime.utcnow().isoformat():
            need.append(i)
    return render_template('admin/index.html', alert_event=need)


###############################################del#
import urllib2
import json
from threading import Thread
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
from app import db
from datetime import datetime

NEW_EVENT_URL = 'http://weplay.tv/lol/bets/ls#game/12/period/all/'


def parse_async_event():
    app = current_app._get_current_object()
    with app.app_context():
        WTV = WeplayTV()
        e = ParseEvent()
        e.add_parser(WTV)
        e.update_data()

        for i in e.event_ids:
            if not Team.query.filter_by(name=e.team1[i]).first():
                addteam_data(e.team1[i])
            if not Team.query.filter_by(name=e.team2[i]).first():
                addteam_data(e.team2[i])
            ev = Event(team1_id=Team.query.filter_by(name=e.team1[i]).first().id,
                       team2_id=Team.query.filter_by(name=e.team2[i]).first().id,
                       date=datetime.fromtimestamp(e.time[i]).replace(hour=datetime.fromtimestamp((e.time[i])).hour-5),
                       team1_k=e.k1[i], team2_k=e.k2[i])
            db.session.add(ev)
            db.session.commit()
        print 'finish'


def parseWTV2():
    if current_user.role != 2:
        return render_template('404.html'), 404
    thr = Thread(target=parse_async_event())
    thr.start()
    return redirect(url_for('events'))


class ParseEvent():
    parsers = []
    event_ids = []
    old_ids = []
    team1 = {}
    team2 = {}
    k1 = {}
    k2 = {}
    time = {}
    result = {}

    def check_id(self, event_id):
        if event_id in self.event_ids:
            return True
        return False

    def add_parser(self, data):
        self.parsers.append(data)

    def add(self, eventid, team1name, team2name, team1k, team2k, time):
        if not self.check_id(eventid):
            self.event_ids.append(eventid)
            self.team1[eventid] = team1name
            self.team2[eventid] = team2name
            self.k1[eventid] = float(team1k)
            self.k2[eventid] = float(team2k)
            self.time[eventid] = int(time)

    def update_data(self):
        for i in self.parsers:
            data = i.get_event_data()
            for j in data:
                self.add(j[0], j[1], j[2], j[3], j[4], j[5])

    def clear(self):
        self.parsers = []
        self.event_ids = []
        self.old_ids = []
        self.self.team1 = {}
        self.team2 = {}
        self.k1 = {}
        self.k2 = {}
        self.time = {}
        self.result = {}


class WeplayTV():
    def get_new_js(self, url):
        html = urllib2.urlopen(url).read()
        file = open('tmp.txt', 'w')
        file.write(html)
        file.close()

        file = open('tmp.txt', 'r')
        flag = False
        for i in file:
            if flag:
                result = i
                break
            if i == '<script id="tbl_content" type="text/template">\n':
                flag = True
        result = result.split(',{"players"')
        for i in xrange(len(result)):
            result[i] = '{"players"' + result[i]
        result[0] = result[0].split('[')[1]
        result[-1] = result[-1].split(']</script>')[0]

        js = []
        for i in result:
            j = json.loads(i)
            if j['players']['cat_id'] == "12":
                js.append(json.loads(i))
        return js

    def get_event_data(self):
        data = self.get_new_js(NEW_EVENT_URL)
        result = []
        for i in data:
            result.append([int(i['players']['event_id']), i['players']['player1'], i['players']['player2'],
                           i['results']['1']['coefficient'], i['results']['3']['coefficient'],
                           i['players']['tm_stamp']])
        return result


if __name__ == '__main__':
    WTV = WeplayTV()
    e = ParseEvent()
    e.add_parser(WTV)
    e.update_data()
else:
    pass
