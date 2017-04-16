from slackclient import SlackClient
import urllib
import json

client_id = "12303250033.170352121623"
client_secret = "af31357db5a31ef574caf66181cd2930"

payload = {
	"status_text": "Please Kill Me",
	"status_emoji": ":stalin:"
}

sc = SlackClient("xoxp-12303250033-12300878704-169665086402-5c30617cf6c9ff283da8bd247f16618c")

kek = sc.api_call(
	"users.profile.set",
	client_id=client_id,
	client_secret=client_secret,
	profile=json.dumps(payload),
	user='U0C8URULQ',
)
print(kek)