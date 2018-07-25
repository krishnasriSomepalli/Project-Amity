# References: https://github.com/Azure-Samples/active-directory-python-webapp-graphapi

from app import app
from flask import render_template, session, Response, request, url_for
from adal import AuthenticationContext
from uuid import uuid4
from app.models import Event, EventRegistrants

PORT = 5000
AUTHORITY_URL = app.config['AUTHORITY_HOST_URL'] + '/' + app.config['TENANT']
REDIRECT_URI = 'http://localhost:{}/getAToken'.format(PORT)
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' + 'response_type=code&client_id={}&redirect_uri={}&' + 'state={}&resource={}')

# interests_list[] data from meetup.com
# CHANGE THIS! THIS SHOULD BE PULLED FROM THE DB!!!
interests_list = ["Outdoors & Adventure", "Tech", "Family", "Health & Wellness", "Sports & Fitness", "Learning", "Photography", "Food & Drink", "Writing", "Language & Culture", "Music", "Movements", "LGBTQ", "Film", "Sci-Fi & Games", "Beliefs", "Arts", "Book Clubs", "Dance", "Pets", "Hobbies & Crafts", "Fashion & Beauty", "Social", "Career & Business"]
selected = ["Tech"]

items = ["Current Events", "Explore", "History", "Create New Event", "Edit Interests"]
alias = 'richard.roe' #get this when the user logs in!!!

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
    pending = []
    todo = []
    events = EventRegistrants.query.filter_by(person_email_alias=alias).all()
    for event in events:
        e_id = event.event_id
        attending = EventRegistrants.query.filter_by(event_id=e_id).count()
        
        details = Event.query.filter_by(event_id=e_id).first()
        people = []
        temp = EventRegistrants.query.filter_by(event_id=e_id).all()
        for obj in temp:
            people.append(obj.person_email_alias)
        print(people)
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
    tempEvents = Event.query.filter((Event.event_status=="pending") | (Event.event_status=="todo")).all() 
    events = []
    for obj in tempEvents:
        attending = EventRegistrants.query.filter_by(event_id=obj.event_id).count()
        if (obj.event_status=="todo" and attending < obj.max_people) or obj.event_status=="pending":
            registered = EventRegistrants.query.filter_by(person_email_alias=alias,event_id=obj.event_id).first()
            if registered is None:
                obj.attending = attending
                events.append(obj)
    return render_template('explore.html', title='Explore', items=items, events=events)
                

@app.route('/history')
def history():
    return render_template('history.html', title='History', items=items)

@app.route('/new')
def new():
    return render_template('new_event.html', title='Create New Event', items=items)

@app.route('/new_event_created', methods=['POST'])
def create():
    return render_template('current_events.html', title='Current Events', items=items)

@app.route('/interests')
def interests():
    return render_template('interests.html', title='Edit Interests', items=items, interests=interests_list, selected=selected)

@app.route('/edit', methods=['POST'])
def edit():
    return render_template('interests.html', title='Edit Interests', items=items, interests=interests_list, selected=selected)