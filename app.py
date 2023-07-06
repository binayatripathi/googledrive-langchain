from __future__ import print_function
from flask import Flask, render_template, url_for, redirect,session,request
from authlib.integrations.flask_client import OAuth
import os

import os.path
import new
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import practise
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
# from practise import get_data
from dotenv import load_dotenv
load_dotenv('.env.local')
app = Flask(__name__)


app.config['SERVER_NAME'] = 'localhost:3000'
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O/<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
oauth = OAuth(app)

@app.route('/')
def index():
    user = session.get('user')
    api_developer_key=os.environ.get('APP_DEVELOPER_KEY')
    api_client_id=os.environ.get('APP_CLIENT_ID')
    # print('------->',user)
    return render_template('index.html',user=user,api_key=api_developer_key,client=api_developer_key)

@app.route('/login')
def google():

	# Google Oauth Config
	# Get client_id and client_secret from environment variables
	# For developement purpose you can directly put it
	# here inside double quotes
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
		name='google',
		client_id=GOOGLE_CLIENT_ID,
		client_secret=GOOGLE_CLIENT_SECRET,
		server_metadata_url=CONF_URL,
		client_kwargs={
			'scope': 'openid email profile https://www.googleapis.com/auth/drive.metadata.readonly'
		}
	)
	
	# Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
	token = oauth.google.authorize_access_token()
	session['user']= token['userinfo']
	return redirect('/')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/folder_id', methods=['GET'])
def get_folderId():
     folder_id = request.args.get('folder_id')
    #  new.check(folder_id)
     print(folder_id)
     return folder_id

@app.route('/get_access', methods=['GET'])
def app_login():
    docs_id = request.args.get('docs_id')
    new.main()
    practise.get_data("what is this file about",docs_id)

    return "login success"
if __name__ == "__main__":
	app.run(debug=True)