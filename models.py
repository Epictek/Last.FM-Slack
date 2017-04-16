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

