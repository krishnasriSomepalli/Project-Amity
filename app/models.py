from app import db
from datetime import datetime

class Event(db.Model):
	__tablename__ = "event"
	event_id = db.Column(db.Integer, primary_key=True, autoincrement='auto')
	event_name = db.Column(db.String(70))
	event_type = db.Column(db.String(21), nullable=False)
	food = db.Column(db.Boolean, nullable=False)
	event_start = db.Column(db.DateTime, nullable=False)
	event_end = db.Column(db.DateTime, nullable=False)
	event_location = db.Column(db.String(105), nullable=False)
	near_to = db.Column(db.String(21), nullable=False)
	min_people = db.Column(db.Integer, nullable=False)
	max_people = db.Column(db.Integer, nullable=False)
	event_desc = db.Column(db.String(280))
	event_status = db.Column(db.String(21), nullable=False)
	creation_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	created_by = db.Column(db.Integer, db.ForeignKey('person.email_alias'))
	def __repr__(self):
		return 'Id: {}\tName: {}\t'.format(self.event_id, self.event_name)

class Person(db.Model):
	__tablename__ = "person"
	email_alias = db.Column(db.String(252), primary_key=True)
	total_events_registered = db.Column(db.Integer, nullable=False)
	total_events_attended = db.Column(db.Integer, nullable=False)
	def __repr__(self):
		return 'Alias: {}\t'.format(self.email_alias)

class Interest(db.Model):
	__tablename__ = "interest"
	interest_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	interest_name = db.Column(db.String(70), nullable=False)
	def __repr__(self):
		return 'Interest: {}\t'.format(self.interest_name)

class EventRegistrants(db.Model):
	__tablename__ = "event_registrants"
	event_registrants_id = db.Column(db.Integer, primary_key=True, autoincrement='auto')
	event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
	person_email_alias = db.Column(db.String(252), db.ForeignKey('person.email_alias'))
	def __repr__(self):
		return 'Event Id: {}\tAlias: {}\t'.format(self.event_id, self.person_email_alias)


class PersonInterests(db.Model):
	__tablename__ = "person_interests"
	person_interests_id = db.Column(db.Integer, primary_key=True, autoincrement='auto')
	person_email_alias = db.Column(db.String(252), db.ForeignKey('person.email_alias'))
	interest_id = db.Column(db.Integer, db.ForeignKey('interest.interest_id'))
	def __repr__(self):
		return 'Alias: {}\tInterest ID: {}\t'.format(self.person_email_alias, self.interest_id)