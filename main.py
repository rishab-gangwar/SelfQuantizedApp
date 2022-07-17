import os
from turtle import update
from flask import Flask, redirect
from flask import render_template, url_for
from flask import request
from flask_sqlalchemy import SQLAlchemy
import matplotlib
import matplotlib.pyplot as plt
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Qselfapp.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

username = ""
flag = 0


class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    trackerused = db.relationship("Trackertype")


class Trackertype(db.Model):
    __tablename__ = 'trackertype'
    trackerID = db.Column(db.Integer, primary_key=True, nullable=False)
    Name = db.Column(db.Text)
    Description = db.Column(db.Text)
    TrackerInV = db.Column(db.Text)
    settings = db.relationship("Setting")
    trackerslog = db.relationship("Trackeradd")
    username = db.Column(db.Text, db.ForeignKey('user.username'))


class Trackeradd(db.Model):
    __tablename__ = 'trackeradd'
    logID = db.Column(db.Integer, primary_key=True, nullable=False)
    When = db.Column(db.Text, unique=True)
    trackerID = db.Column(db.Integer, db.ForeignKey('trackertype.trackerID'))
    Value = db.Column(db.Text)
    Notes = db.Column(db.Text)


class Setting(db.Model):
    __tablename__ = 'setting'
    setting_id = db.Column(db.Integer, primary_key=True)
    trackerID = db.Column(db.Integer, db.ForeignKey('trackertype.trackerID'))
    setting = db.Column(db.Integer)


@ app.route("/", methods=['GET', 'POST'])
def home():
    global username, flag
    if request.method == "GET" and not flag:
        flag = 1
        return(render_template("login.html"))

    elif request.method == "GET":
        Tracker = Trackertype.query.filter_by(username=username).all()
        # print(Tracker["Name"])
        empt = Tracker == []
        return render_template("Dashboard.html", username=username, Trackertype=Tracker, empt=empt)

    if request.method == "POST":
        username = request.form.get("loginname")
        print(username)
        Tracker = Trackertype.query.filter_by(username=username).all()
        # print(Tracker["Name"])
        empt = Tracker == []
        return render_template("Dashboard.html", username=username, Trackertype=Tracker, empt=empt)


@ app.route("/trackertype/create", methods=['GET', 'POST'])
def create():
    if request.method == "GET":
        return render_template("createnewTracker.html", username=username)
    if request.method == "POST":
        name = request.form.get("name")
        print(name)
        description = request.form.get("description")
        Type = request.form.get("type")
        settings = request.form.get('setting')
        print(settings, Type)
        if Type == "Multiple":
            settings = settings.split(",")
        print(settings)
        is_tracker = Trackertype.query.filter_by(
            Name=name, username=username).all()
        print(is_tracker)
        if not request.form['name'] or not request.form['description'] or (Type == "Multiple" and settings == []):
            print('Please enter all the fields', 'error')
        elif(not (is_tracker == [])):
            return render_template("createdalready.html", username=username)
        else:
            newTrackertype = Trackertype(
                Name=name, Description=description, TrackerInV=Type, username=username)

            db.session.add(newTrackertype)
            db.session.commit()
            print(Type)
            if Type == "Multiple":
                for element in settings:
                    setting = Setting(
                        trackerID=newTrackertype.trackerID, setting=element)
                    db.session.add(setting)
                    db.session.commit()
                return redirect(url_for('home'))
            else:
                return redirect(url_for('home'))
    return render_template('dashboard.html', username=username)


@ app.route("/trackertype/<trackertypename>/delete", methods=['GET', 'POST'])
def trackertypedelete(trackertypename):
    Tracker = Trackertype.query.filter_by(Name=trackertypename).first()
    trackerid = Tracker.trackerID
    Trackerlogs = Trackeradd.query.filter_by(trackerID=trackerid).all()
    for Trackerlog in Trackerlogs:
        db.session.delete(Trackerlog)
        db.session.commit()
    settings = Setting.query.filter_by(trackerID=trackerid).all()
    for setting in settings:
        db.session.delete(setting)
        db.session.commit()
    print(Tracker)
    if Tracker != type(None):
        db.session.delete(Tracker)
        db.session.commit()

    return redirect(url_for('home'))


@ app.route("/logout", methods=['GET', 'POST'])
def logout():
    global flag
    flag = 0
    return redirect(url_for('home'))


@ app.route("/trackertype/<trackerid>/update", methods=['GET', 'POST'])
def trackertypeupdate(trackerid):
    if request.method == "GET":
        Tracker = Trackertype.query.filter_by(trackerID=trackerid).first()
        print(Tracker)
        trackerid = Tracker.trackerID
        name = Tracker.Name
        description = Tracker.Description
        trackerinv = Tracker.TrackerInV
        Trackerlogs = Trackeradd.query.filter_by(trackerID=trackerid).all()
        for Trackerlog in Trackerlogs:
            db.session.delete(Trackerlog)
            db.session.commit()
        settings = Setting.query.filter_by(trackerID=trackerid).all()
        for setting in settings:
            db.session.delete(setting)
            db.session.commit()
        print(Tracker)
        if Tracker != type(None):
            db.session.delete(Tracker)
            db.session.commit()
        return(render_template("updatetracker.html", username=username, trackerid=trackerid, name=name, description=description, trackerinv=trackerinv))
    if request.method == "POST":
        name = request.form.get("name")
        print(name)
        description = request.form.get("description")
        intype = request.form.get("type")
        updatedTrackertype = Trackertype(
            Name=name, Description=description, TrackerInV=intype, username=username)
        db.session.add(updatedTrackertype)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=username)


@ app.route("/trackertype/<trackertypename>/create", methods=['GET', 'POST'])
def trackerlogcreate(trackertypename):
    tracker = Trackertype.query.filter_by(Name=trackertypename).first()
    trackerid = tracker.trackerID
    if request.method == "GET":
        is_multiple = "Multiple" == tracker.TrackerInV
        settings = []
        if is_multiple:
            settingsq = Setting.query.filter_by(trackerID=trackerid).all()
            for i in settingsq:
                settings.append(i.setting)
        print(settings)
        return render_template("trackerlog.html", username=username, multiple=is_multiple, settings=settings, name=trackertypename)
    if request.method == "POST":
        when = request.form.get("when")
        value = request.form.get("value")
        note = request.form.get("notes")
        newTrackertype = Trackeradd(
            When=when, trackerID=trackerid, Value=value, Notes=note)
        db.session.add(newTrackertype)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=username)


@ app.route("/trackertype/<trackerid>", methods=['GET', 'POST'])
def trackerinfo(trackerid):
    selectedtrackerlog = Trackeradd.query.filter_by(trackerID=trackerid).all()
    tracker = Trackertype.query.filter_by(trackerID=trackerid).first()
    print(tracker.Name)
    when = []
    logids = []
    values = []
    notes = []
    if tracker.TrackerInV == "Num":
        for each in selectedtrackerlog:

            logids.append(each.logID)
            ans = each.When
            ans = ans.replace('T', ' \nat ')
            when.append(ans)
            notes.append(each.Notes)
            values.append(int(each.Value))
        plt.scatter(when, values)
    else:
        for each in selectedtrackerlog:
            logids.append(each.logID)
            ans = each.When
            ans = ans.replace('T', ' \nat ')
            when.append(ans)
            notes.append(each.Notes)
            values.append(each.Value)
        plt.hist(values)
    plot = f'static/img/{trackerid}'
    plt.savefig(plot)
    plt.close()
    return(render_template("trackerinfo.html", username=username, plot=f'{trackerid}.png', trackerid=trackerid, when=when, notes=notes, values=values, n=len(values), trackername=tracker.Name, whenorig=logids))


@ app.route("/trackerlog/<logid>/delete")
def logdelete(logid):
    selectedlog = Trackeradd.query.filter_by(
        logID=logid).all()
    print(selectedlog)
    trackerid = 0
    for i in selectedlog:
        trackerid = i.trackerID
        db.session.delete(i)
        db.session.commit()
    print(url_for('home'), request.base_url)
    return redirect(f'http://localhost:5000/trackertype/{trackerid}')


@ app.route("/trackerlog/<logid>/update")
def logupdate(logid):
    if request.method == "GET":
        selectedlog = Trackeradd.query.filter_by(
            logID=logid).first()
        tracker = Trackertype.query.filter_by(
            trackerID=selectedlog.trackerID).first()
        trackerid = tracker.trackerID
        invalue = tracker.TrackerInV
        selectedlog = Trackeradd.query.filter_by(
            logID=logid).all()
        print(selectedlog)
        trackerid = 0
        value = ""
        when = ""
        for i in selectedlog:
            value = i.Value
            when = i.When
            trackerid = i.logID
            db.session.delete(i)
            db.session.commit()
        if request.method == "GET":
            is_multiple = "Multiple" == invalue
            settings = []
            if is_multiple:
                settingsq = Setting.query.filter_by(trackerID=trackerid).all()
                for i in settingsq:
                    settings.append(i.setting)
            return render_template("updatelog.html", username=username, multiple=is_multiple, settings=settings, name=tracker.Name, oldvalue=value, oldwhen=when)
    if request.method == "POST":
        selectedlog = Trackeradd.query.filter_by(
            logID=logid).all()
        print(selectedlog)
        trackerid = 0
        for i in selectedlog:
            trackerid = i.logid
            db.session.delete(i)
            db.session.commit()

        when = request.form.get("when")
        value = request.form.get("value")
        note = request.form.get("notes")
        newTrackerlog = Trackeradd(logID=logid,
                                   When=when, trackerID=trackerid, Value=value, Notes=note)
        db.session.add(newTrackerlog)
        db.session.commit()
        print(url_for('home'), request.base_url)
    return redirect(f'http://localhost:5000/trackertype/{trackerid}')


if __name__ == '__main__':
    app.run(debug=True)
