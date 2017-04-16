import os
from flask import Flask, request, jsonify
from slackclient import SlackClient
import urllib
import json
from flask_sqlalchemy import SQLAlchemy
import pylast

last_api_key = os.environ["LAST_API_KEY"]
last_api_secret = os.environ["LAST_API_SECRET"]

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]

lastfm_network = pylast.LastFMNetwork(api_key=last_api_key, api_secret=last_api_secret)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(9))
    team_id = db.Column(db.String(9))
    user_token = db.Column(db.String(74))
    user_status = db.Column(db.String(80))
    lastfm = db.Column(db.String(15))
    def __init__(self,user_id,team_id, user_token=None, user_status=None, lastfm=None):
        self.user_id = user_id
        self.team_id = team_id
        self.user_token = user_token
        self.user_status = user_status
        self.lastfm = lastfm

    def __repr__(self):
        return '<User %r>' % self.user_id

@app.route("/nowplaying", methods=["POST"])
def nowplaying():
    username = "@" + request.form.get('user_name', None)
    user_id = request.form.get('user_id', None)
    lastfm_user = request.form.get('text', None)
    if lastfm_user == "" or lastfm_user == None:
       user = User.query.filter_by(user_id=user_id).first()
       if user == None:
           return "Please enter a valid username", 200
       lastfm_user = user.lastfm
       if lastfm_user == None:
           return "Please enter a valid username", 200
    np = lastfm_network.get_user(lastfm_user).get_now_playing()
    if np == None:
        return "No song playing.", 200
    payload = {
        "response_type": "in_channel",
        "text": "<http://last.fm/user/" + lastfm_user + "|" +  lastfm_user + "> is currently listening to <" + np.get_url() + "|" + np.artist.name + " - " + np.title + ">",
        "unfurl_links": False
    }
    return jsonify(payload), 200

@app.route("/auth", methods=["GET", "POST"])
def pre_install():
    token = request.form.get('token', None)  # TODO: validate the token
    text = request.form.get('text', None)   
    if text == None or text == "":
        return "please enter a valid user", 200
    return '<https://slack.com/oauth/authorize?scope=users.profile:write,users.profile:read&client_id=12303250033.170352121623&redirect_uri=' + urllib.parse.quote ('https://1e2e4665.ngrok.io/finish_auth') + '&state=' + text + '| Click here to Sign in with Slack!>', 200

@app.route("/finish_auth/", methods=["GET", "POST"])
def post_install():
    lastfm_user = request.args['state']
    print(lastfm_user)
      # Retrieve the auth code from the request params
    auth_code = request.args['code']

      # An empty string is a valid token for this request
    sc = SlackClient("")

      # Request the auth tokens from Slack
    auth_response = sc.api_call(
        "oauth.access",
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )
    print(auth_response)
    user_id = auth_response['user_id']
    team_id = auth_response['team_id']
    token = auth_response['access_token']
    
    user = User.query.filter_by(user_id=user_id).first()
    if user == None:
        profile = sc.api_call(
            "users.profile.get",
            client_id=client_id,
            team_id=team_id,
            client_secret=client_secret,
            user=user_id
        )

        currentProfile = {
            "status_text": profile['profile']['status_text'],
            "status_emoji": profile['profile']['status_emoji']
        }

        user = User(user_id, team_id, token, json.dumps(currentProfile), lastfm_user)
        db.session.add(user)
        db.session.commit()

    else:
        user.lastfm = lastfm_user
        db.session.commit()
        return "Updated LastFM user."
    return "Auth Complete, Added LastFM user."

if __name__ == "__main__":
    app.run(debug=True)