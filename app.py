import json
import pylast
from time import sleep
import urllib
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from slackclient import SlackClient
from time import sleep
import os

last_api_key = os.environ["LAST_API_KEY"]
last_api_secret = os.environ["LAST_API_SECRET"]

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]


db = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=db)

Base = declarative_base()
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(9))
    team_id = Column(String(9))
    user_token = Column(String(74))
    user_status = Column(String(80))
    lastfm = Column(String(15))
    def __init__(self,user_id,team_id, user_token=None, user_status=None, lastfm=None):
        self.user_id = user_id
        self.team_id = team_id
        self.user_token = user_token
        self.user_status = user_status
        self.lastfm = lastfm
    def __repr__(self):
        return '<User %r>' % self.user_id


lastfm_network = pylast.LastFMNetwork(api_key=last_api_key, api_secret=last_api_secret)

def setStatus(user):
    np = lastfm_network.get_user(user.lastfm).get_now_playing()
    sc = SlackClient(user.user_token)
    response = sc.api_call(
        "users.profile.get",
        client_id=client_id,
        team_id=user.team_id,
        client_secret=client_secret,
        user=user.user_id
    )

    currentProfile = {
        "status_text": response['profile']['status_text'],
        "status_emoji": response['profile']['status_emoji']
    }

    if user.user_status == None:
        user.user_status = json.dumps(currentProfile)


    if np != None:
        song = np.artist.name + " - " + np.title
        song = (song[:97] + '...') if len(song) > 100 else song
        if song == response['profile']['status_text']:
            return
        if response['profile']['status_emoji'] != ":musical_note:":
            user.user_status = json.dumps(currentProfile)
        payload = {
            "status_text": song,
            "status_emoji": ":musical_note:"
        }
    else:
        if json.loads(user.user_status)['status_text'] == response['profile']['status_text']:
            return
        if response['profile']['status_emoji'] == ":musical_note:":
            payload = {
                "status_text": json.loads(user.user_status)['status_text'],
                "status_emoji": json.loads(user.user_status)['status_emoji']
            }
        else:
            user.user_status = json.dumps(currentProfile)
            return
    print("Updated " + user.user_id + " status to:")
    print(payload)
    response = sc.api_call(
        "users.profile.set",
        client_id=client_id,
        team_id=user.team_id,
        client_secret=client_secret,
        profile=json.dumps(payload),
        user=user.user_id
    )
    return True

def main():
    session = Session()
    for user in session.query(User).yield_per(10):
        setStatus(user)
    session.commit()

if __name__ == "__main__":
    while True:
        main()
        sleep(5)