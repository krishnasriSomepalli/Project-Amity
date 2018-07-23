import os

class Config(object):
	TENANT = os.environ.get('TENANT') or 'tenant-name'
	CLIENT_SECRET = os.environ.get('CLIENT_SECRET') or 'client-secret'
	CLIENT_ID = os.environ.get('CLIENT_ID') or 'client-id'