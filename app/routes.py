# References: https://github.com/Azure-Samples/active-directory-python-webapp-graphapi

from app import app, db
from flask import render_template, session, Response, request, url_for, redirect
from datetime import datetime
from adal import AuthenticationContext
from uuid import uuid4
from app.models import Event, EventRegistrants, Interest, PersonInterests

#db = SQLAlchemy()

PORT = 5000
AUTHORITY_URL = app.config['AUTHORITY_HOST_URL'] + '/' + app.config['TENANT']
REDIRECT_URI = 'http://localhost:{}/getAToken'.format(PORT)
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' + 'response_type=code&client_id={}&redirect_uri={}&' + 'state={}&resource={}')

items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
alias = 'richard.roe' #get this when the user logs in!!!

# interests_list[] data from meetup.com
interests_list = list(map(lambda interest: interest.interest_name, Interest.query.all()))
selected = list(map(lambda interest: interests_list[interest.interest_id-1], PersonInterests.query.filter_by(person_email_alias=alias).all()))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
@app.route('/signup')
def authorize():
    auth_state = str(uuid4())
    session['state'] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        app.config['TENANT'],
        app.config['CLIENT_ID'],
        REDIRECT_URI,
        auth_state,
        app.config['RESOURCE'])
    resp = Response(status=307)
    resp.headers['location'] = authorization_url
    return resp

@app.route('/getAToken')
def get_token():
    code = request.args['code']
    state = request.args['state']
    if state != session['state']:
        raise ValueError("State does not match")
    auth_context = AuthenticationContext(AUTHORITY_URL)
    token_response = auth_context.acquire_token_with_authorization_code(code, REDIRECT_URI, app.config['RESOURCE'], app.config['CLIENT_ID'], app.config['CLIENT_SECRET'])
    session['access_token'] = token_response['accessToken']
    return flask.redirect('/graphcall')

@app.route('/graphcall')
def graphcall():
    if 'access_token' not in session:
        return flask.redirect(url_for('/login'))
    endpoint = app.config['RESOURCE'] + '/' + app.config['API_VERSION'] + '/me/'
    http_headers = {'Authorization': session.get('access_token'),
                    'User-Agent': 'adal-python-sample',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid4())}
    graph_data = request.get(endpoint, headers=http_headers, stream=False).json()
    return render_template('display_graph_info.html', graph_data=graph_data)


@app.route('/running')
def running():
    # array of pending events
    pending = []
    # array of todo events
    todo = []
    # array of all events that the logged-in person is associated with
    events = EventRegistrants.query.filter_by(person_email_alias=alias).all()
    for event in events:
        e_id = event.event_id
        # number of people attending the event with event ID e_id
        attending = EventRegistrants.query.filter_by(event_id=e_id).count()
        # event (with event ID e_id)
        details = Event.query.filter_by(event_id=e_id).first()
        # array of people associated with event ID e_id
        people = []
        # all event-person mappings (EventRegistrants) with event ID e_id
        people = list(map(lambda mapping: mapping.person_email_alias, EventRegistrants.query.filter_by(event_id=e_id).all()))    
        print(people)
        # updating details of the event, using other tables, and populating 'todo' and 'pending', depending on the status of that event 
        if details.event_status == "pending":
            details.people = people
            details.attending = attending
            pending.append(details)
        elif details.event_status == "todo":
            details.people = people
            details.attending = attending
            todo.append(details)
    return render_template('current_events.html', title='Current Events', items=items, pending=pending, todo=todo)

@app.route('/explore')
def explore():
    # pulling all events with status 'pending' or 'todo'
    tempEvents = Event.query.filter((Event.event_status=="pending") | (Event.event_status=="todo")).all() 
    # populate with the events to show the user; pending/accomodable todo events they could join
    explore_events = []
    for obj in tempEvents:
        # number of people associated with obj.event_id
        attending = EventRegistrants.query.filter_by(event_id=obj.event_id).count()
        # if this event can accomodate more people
        if (obj.event_status=="todo" and attending < obj.max_people) or obj.event_status=="pending":
            # event-person mapping for this event and the logged-in person; helps answer whether the logged-in person is attending this event or not, and thus if we need to include this in events[]
            registered = EventRegistrants.query.filter_by(person_email_alias=alias,event_id=obj.event_id).first()
            if registered is None and obj.event_start < datetime.utcnow():
                obj.attending = attending
                explore_events.append(obj)
    return render_template('explore.html', title='Explore', items=items, events=explore_events)
                

@app.route('/history')
def history():
    # get all events that have been completed: get all events this person is associated with; get events that are completed
    people_met = []
    # using IDs of these events, get the list of all people who've attended these
    past_events = []
    associated_event_mappings = EventRegistrants.query.filter_by(person_email_alias=alias).all()
    associated_events = []
    for mapping in associated_event_mappings:
        e_id = mapping.event_id
        details = Event.query.filter_by(event_id=e_id).first()
        if details.event_end < datetime.utcnow():
            people = list(map(lambda mapping: mapping.person_email_alias, EventRegistrants.query.filter_by(event_id=e_id).all()))
            details.people = people
            past_events.append(details)
            people_met = list(map(lambda mapping: mapping.person_email_alias, EventRegistrants.query.filter_by(event_id=e_id).all()))
    print(people_met)
    print(past_events)
    return render_template('history.html', title='History', items=items, people=people_met, events=past_events)

@app.route('/new')
def new():
    return render_template('new_event.html', title='Create New Event', items=items)

@app.route('/new_event_created', methods=['POST'])
def create():
    return render_template('current_events.html', title='Current Events', items=items)

@app.route('/interests')
def interests():
    selected = list(map(lambda interest: interests_list[interest.interest_id-1], PersonInterests.query.filter_by(person_email_alias=alias).all()))
    return render_template('interests.html', title='Edit Interests', items=items, interests=interests_list, selected=selected)

@app.route('/edit', methods=['POST'])
def edit():
    selected_updated_id = list(map(lambda name: name.replace("interest", ""), request.form))
    PersonInterests.query.filter_by(person_email_alias=alias).delete()
    db.session.commit()
    for update in selected_updated_id:
        new = PersonInterests(person_email_alias=alias, interest_id=update)
        print(interests_list[int(update)-1])
        db.session.add(new)
    db.session.commit()
    return redirect(url_for('interests'))