from datetime import datetime, timedelta
from urllib.parse import urljoin

from django.utils import timezone

import json
import requests

from p0sx.settings.base import SITE_URL, SUMUP_CALLBACK_HOSTNAME, SUMUP_MERCHANT_CODE


API_URL = 'https://api.sumup.com/'


def update_transactions(api_key, seconds=300):
    if api_key.token_expired:
        api_key.refresh_current_token()
    url = urljoin(API_URL, '/v0.1/me/transactions/history')
    data = {
        'changes_since': (datetime.now() - timedelta(seconds=seconds)).isoformat()
    }
    req = requests.get(
        url=url,
        data=data,
        headers={'Authorization': 'Bearer {}'.format(api_key.token)}
    )
    transactions = []
    for item in req.json()['items']:
        trans, created = api_key.transactions.get_or_create(
            transaction_id=item['transaction_id'],
            defaults={
                'user': item['user'],
                'status': item['status'],
                'summary': item.get('product_summary', ''),
                'transaction_code': item['transaction_code'],
                'amount': item['amount'],
                'timestamp': item['timestamp']
            }
        )
        if not created and trans.status != item['status']:
            trans.status = item['status']
            trans.save()
        transactions.append(trans.pk)
    return api_key.transactions.filter(pk__in=transactions)


def fetch_transaction_status(api_key, txid):
    if api_key.token_expired:
        api_key.refresh_current_token()
    url = urljoin(API_URL, '/v0.1/me/transactions')
    data = {
        'transaction_code': txid
    }
    req = requests.get(
        url=url,
        data=data,
        headers={'Authorization': 'Bearer {}'.format(api_key.token)}
    )
    td = req.json()
    if 'status' in td:
        if td['status'] == 'SUCCESSFUL':
            return True
    else:
        return False


def fetch_onlinetransaction_status(api_key, tid):
    if api_key.token_expired:
        api_key.refresh_current_token()
    url = urljoin(API_URL, '/v0.1/checkouts/' + tid)
    req = requests.get(
        url=url,
        headers={'Authorization': 'Bearer {}'.format(api_key.token)}
    )
    td = req.json()
    print(td)
    if 'status' in td:
        if td['status'] == 'PAID':
            return True
    else:
        return False


def refresh_token(api_key):
    req = requests.post(
        url=urljoin(API_URL, 'token'),
        data={
            'grant_type': 'refresh_token',
            'client_id': api_key.client_id,
            'client_secret': api_key.client_secret,
            'refresh_token': api_key.refresh_token
        }
    )
    ret = req.json()
    api_key.token = ret['access_token']
    api_key.token_expiry = timezone.now() + timedelta(seconds=ret['expires_in'])
    api_key.refresh_token = ret['refresh_token']
    api_key.refresh_token_expiry = timezone.now() + timedelta(days=180)
    print(ret['scope'])
    api_key.save()


def create_checkout(api_key, tid, amount, phone):
    if api_key.token_expired:
        api_key.refresh_current_token()
    req = requests.post(
        url=urljoin(API_URL, '/v0.1/checkouts'),
        headers={'Authorization': 'Bearer {}'.format(api_key.token)},
        data={
            'checkout_reference': str(tid),
            'amount': amount,
            'currency': 'NOK',
            'merchant_code': SUMUP_MERCHANT_CODE,
            'return_url': SUMUP_CALLBACK_HOSTNAME + 'callbackonline/' + str(tid),
            'description': 'PolarPæng Online ' + phone
            #'redirect_url': SITE_URL + 'littleadmin/sumup-return/'  # + str(tid)
        }
    )
    ret = req.json()

    if ret['id']:
        txid = ret['id']
        return txid

    else:
        return False
