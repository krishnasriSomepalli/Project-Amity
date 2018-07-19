from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Amity')

@app.route('/running')
def running():
	items = ["Current Events", "Explore", "History", "Join New Event", "Edit Interests"]
	return render_template('sidebar.html', title='Current Events', items=items)