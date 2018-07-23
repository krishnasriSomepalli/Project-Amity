import os

class Config(object):
	AUTHORITY_HOST_URL = "https://login.microsoft.com"
	CLIENT_ID = os.environ.get('CLIENT_ID') or 'client-id'
	CLIENT_SECRET = os.environ.get('CLIENT_SECRET') or 'client-secret'
	RESOURCE = "https://graph.microsoft.com/"
	TENANT = os.environ.get('TENANT') or 'tenant-name'

	SECRET_KEY = os.environ.get('SECRET_KEY') or 'fubar'