from app import app
from flask import render_template

# interests_list[] data from meetup.com
interests_list = ["Outdoors & Adventure", "Tech", "Family", "Health & Wellness", "Sports & Fitness", "Learning", "Photography", "Food & Drink", "Writing", "Language & Culture", "Music", "Movements", "LGBTQ", "Film", "Sci-Fi & Games", "Beliefs", "Arts", "Book Clubs", "Dance", "Pets", "Hobbies & Crafts", "Fashion & Beauty", "Social", "Career & Business"]
selected = ["Tech"]

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Amity')

@app.route('/running')
def running():
	items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
	return render_template('current_events.html', title='Current Events', items=items)

@app.route('/explore')
def explore():
	items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
	return render_template('explore.html', title='Explore', items=items)

@app.route('/history')
def history():
	items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
	return render_template('history.html', title='History', items=items)

@app.route('/new')
def new():
	items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
	return render_template('new_event.html', title='Create New Event', items=items)

@app.route('/new_event_created', methods=['POST'])
def create():
	items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
	return render_template('current_events.html', title='Current Events', items=items)

@app.route('/interests')
def interests():
	items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
	return render_template('interests.html', title='Edit Interests', items=items, interests=interests_list, selected=selected)

@app.route('/edit', methods=['POST'])
def edit():
	items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
	return render_template('interests.html', title='Edit Interests', items=items, interests=interests_list, selected=selected)