from django.conf import settings

import requests

EVENT_ID = settings.GE_EVENT_ID
API_URL = 'https://geekevents.org/sso'

def get_user(user_id, timestamp, token):
    url = API_URL + '/userinfo/'
    data = {
        'user_id': user_id,
        'token': token,
        'timestamp': timestamp,
        'event_id': EVENT_ID
    }
    req = requests.post(
        url=url,
        data=data
    )

    user = req.json()

    return user

def user_has_ticket(user_id, timestamp, token):
    url = API_URL + '/user-has-ticket/'
    data = {
        'user_id': user_id,
        'token': token,
        'timestamp': timestamp,
        'event_id': EVENT_ID
    }
    try:
        req = requests.post(
            url=url,
            data=data
        )

        return int(req.content) > 0
    except:
        return False

def validate_token(user_id, timestamp, token):
    url = API_URL + '/validate/'
    data = {
        'user_id': user_id,
        'token': token,
        'timestamp': timestamp
    }
    try:
        req = requests.post(
            url=url,
            data=data
        )
        result = req.json()
    except:
        return False

    return result["status"]
