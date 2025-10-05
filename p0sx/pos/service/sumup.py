from datetime import datetime, timedelta
from urllib.parse import urljoin

from django.utils import timezone

import json
import requests

from p0sx.settings.base import SITE_URL, SUMUP_CALLBACK_HOSTNAME, SUMUP_MERCHANT_CODE, SUMUP_BEARER_TOKEN, EVENT_NAME


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

def init_order_card_payment(order, reader_id):
    """
    Initializes payment with a SumUp terminal
    """
    # curl example:
    """
    curl -X POST   -H "Content-Type: application/json"   -H "Authorization: Bearer BEARER-TOKEN"
    -d '{
    "total_amount": {
      "value": 100,
      "currency": "NOK",
      "minor_unit": 2
    },
    "description": "testbetaling gjort frå kommandolinje",
    }
    '   https://api.sumup.com/v0.1/merchants/MERCHANT_ID/readers/READER_ID/checkout
    """
    payload = {
        "total_amount": {"value": int(order.sum * 100), "currency": "NOK", "minor_unit": 2},
        "description": f"{EVENT_NAME} p0sX ordre {order.pk}",
        "return_url":  SUMUP_CALLBACK_HOSTNAME + '/order-callback/' + str(order.pk),
    }
    url = f"https://api.sumup.com/v0.1/merchants/{SUMUP_MERCHANT_CODE}/readers/{reader_id}/checkout"
    headers = {"Authorization": f"Bearer {SUMUP_BEARER_TOKEN}"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        order.payment_reference = response.json()["data"]["client_transaction_id"]
        order.save()
    return response.json()


def get_sumup_transaction(transaction_id):
    headers = {"Authorization": f"Bearer {SUMUP_BEARER_TOKEN}"}
    url = f"https://api.sumup.com/v2.1/merchants/{SUMUP_MERCHANT_CODE}/transactions?client_transaction_id={transaction_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def pair_sumup_reader(name, pairing_code):
    payload = {
        "name": name,
        "pairing_code": pairing_code
    }
    url = f"https://api.sumup.com/v0.1/merchants/{SUMUP_MERCHANT_CODE}/readers"
    headers = {"Authorization": f"Bearer {SUMUP_BEARER_TOKEN}"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        return response.json()["id"]
    return None

def delete_sumup_reader(reader_id):
    url = f"https://api.sumup.com/v0.1/merchants/{SUMUP_MERCHANT_CODE}/readers/{reader_id}"
    headers = {"Authorization": f"Bearer {SUMUP_BEARER_TOKEN}"}
    response = requests.delete(url, headers=headers)
    return response.status_code
