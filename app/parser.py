import urllib2
import json
from threading import Thread
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from models import Team, Event
# from admin.views import addteam_data
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
                       team2_id=Team.query.filter_by(name=e.team2[i]).first().id, date=datetime.fromtimestamp(e.time[i]),
                       team1_k=e.k1[i], team2_k=e.k2[i])
            db.session.add(ev)
            db.session.commit()
        print 'finish'


def parseWTV2():
    if current_user.role != 2:
        return render_template('404.html'), 404
    thr = Thread(target=parse_async_event())
    thr.start()
    return redirect(request.args.get('next') or url_for('index'))



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
