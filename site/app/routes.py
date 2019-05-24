from app import app, db, mqtt, photos
from flask import render_template, redirect, url_for, flash
from app.forms import RegisterUserForm, RegisterCheckpointForm, LoginForm, RegisterRaceForm
from app.models import User, Event, Race
from flask_login import current_user, login_user, logout_user

events_col = db.events
races_col = db.races


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if (current_user.is_authenticated):
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		if form.username.data == 'admin' and form.password.data == 'admin':
			user = User()
			user.username = 'admin'
			user.password = 'admin'
			user.role = 'admin'
			user.id = 1
			login_user(user)
			flash('{}  authorized! Welcome!'.format(user.username))
			return redirect(url_for('index'))
		elif form.username.data == 'organizer' and form.password.data == 'organizer':
			user = User()
			user.username = 'organizer'
			user.password = 'organizer'
			user.role = 'organizer'
			user.id = 2
			login_user(user)
			flash('{} authorized! Welcome!'.format(user.username))
			return redirect(url_for('index'))
		else:
			flash('Invalid username or password')
			return redirect(url_for('login'))
	return render_template('login.html', form=form)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
	mqtt.subscribe('myTopic')


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
	payload=message.payload.decode().split(' ')
	payload[0]=payload[0].strip()
	payload[2]+=(' ' + payload[3])
	payload.pop()
	print(payload)
	event = Event(payload[0], payload[1], payload[2])
	events_col.insert({"checkpoint_id":event.checkpoint_id, "tag":event.tag, "time":event.time})


@app.route("/clear")
def clear():
	events_col.remove()
	return redirect("/results")


@app.route("/results")
def table():
	heading = "Table with events"

	list = []
	for events in events_col.find() :
	   list.append(events)
	list.reverse()
	return render_template("table.html",events = list, h=heading)


@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
	if (current_user.is_anonymous):
		return redirect(url_for('index'))
	form = RegisterUserForm()
	if form.validate_on_submit():
		flash('User {} {} is successfully registered.'.format(form.first_name.data, form.last_name.data))
		return redirect(url_for('index'))
	return render_template('register_user.html', form=form)


@app.route('/register_checkpoint', methods=['GET', 'POST'])
def register_checkpoint():
	if (current_user.is_anonymous):
		return redirect(url_for('index'))
	form = RegisterCheckpointForm()
	if form.validate_on_submit():
		flash('Checkpoint {} is successfully registered.'.format(form.name.data))
		return redirect(url_for('index'))
	return render_template('register_checkpoint.html', form=form)

@app.route('/register_race', methods=['GET', 'POST'])
def register_race():
	if (current_user.is_anonymous):
		return redirect(url_for('index'))
	form = RegisterRaceForm()
	form.laps_number.choices = [(i, i) for i in range(1,11)]
	if form.validate_on_submit():
		#filename = photos.save(form.logo.data)
		race = Race(form.name.data, form.admin.data, form.laps_number.data, form.lap_length.data, form.date_and_time_of_race.data, form.description.data)
		races_col.insert({"name":race.name, "admin":race.admin, "laps_number":race.laps_number,
			"lap_length":race.lap_length, "date_and_time_of_race":race.date_and_time_of_race, "description":race.description})
		flash('Race {} is successfully registered.'.format(form.name.data))
		return redirect(url_for('index'))
	return render_template('register_race.html', form=form)

@app.route("/races")
def races():
	heading = "Table with races"

	list = []
	for race in races_col.find():
	   list.append(race)
	list.reverse()
	return render_template("races.html",races = list, h=heading)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
