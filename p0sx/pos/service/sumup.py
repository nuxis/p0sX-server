import requests

from django.conf import settings


API_URL = 'https://api.sumup.com/'

def init_order_card_payment(order, reader_id):
    """
    Initializes payment with a SumUp terminal
    """
    payload = {
        "total_amount": {"value": int(order.sum * 100), "currency": "NOK", "minor_unit": 2},
        "description": f"{settings.EVENT_NAME} p0sX ordre {order.pk}",
        "return_url":  settings.SUMUP_CALLBACK_HOSTNAME + '/order-callback/' + str(order.pk),
    }
    url = f"https://api.sumup.com/v0.1/merchants/{settings.SUMUP_MERCHANT_CODE}/readers/{reader_id}/checkout"
    headers = {"Authorization": f"Bearer {settings.SUMUP_BEARER_TOKEN}"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        order.payment_reference = response.json()["data"]["client_transaction_id"]
        order.save()
    return response.json()

def init_credit_fill_payment(transaction, reader_id):
    """
    Initializes payment with a SumUp terminal
    """
    payload = {
        "total_amount": {"value": int(transaction.amount * 100), "currency": "NOK", "minor_unit": 2},
        "description": f"{settings.EVENT_NAME} P0sX påfyll for {transaction.user.card} - {transaction.pk}",
        "return_url":  settings.SUMUP_CALLBACK_HOSTNAME + '/credit-callback/' + str(transaction.pk),
    }
    url = f"https://api.sumup.com/v0.1/merchants/{settings.SUMUP_MERCHANT_CODE}/readers/{reader_id}/checkout"
    headers = {"Authorization": f"Bearer {settings.SUMUP_BEARER_TOKEN}"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        transaction.payment_reference = response.json()["data"]["client_transaction_id"]
        transaction.save()
    return response.json()

def get_sumup_transaction(transaction_id):
    headers = {"Authorization": f"Bearer {settings.SUMUP_BEARER_TOKEN}"}
    url = f"https://api.sumup.com/v2.1/merchants/{settings.SUMUP_MERCHANT_CODE}/transactions?client_transaction_id={transaction_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def pair_sumup_reader(name, pairing_code):
    payload = {
        "name": name,
        "pairing_code": pairing_code
    }
    url = f"https://api.sumup.com/v0.1/merchants/{settings.SUMUP_MERCHANT_CODE}/readers"
    headers = {"Authorization": f"Bearer {settings.SUMUP_BEARER_TOKEN}"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        return response.json()["id"]
    return None

def delete_sumup_reader(reader_id):
    url = f"https://api.sumup.com/v0.1/merchants/{settings.SUMUP_MERCHANT_CODE}/readers/{reader_id}"
    headers = {"Authorization": f"Bearer {settings.SUMUP_BEARER_TOKEN}"}
    response = requests.delete(url, headers=headers)
    return response.status_code
