import requests
import os
import json

def send_message(message: str):
    webhook_url = os.environ['DISCORD_WEBHOOK']
    data = {}
    data["content"] = message
    data["username"] = "Finn House Scraping"
    result = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
