from tabnanny import check
import uuid
from datetime import timedelta
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from pos.models.sumup import SumUpAPIKey, SumUpCard, SumUpOnline
from pos.service.sumup import API_URL, fetch_onlinetransaction_status, fetch_transaction_status

import json
import requests


@permission_required('pos.update_credit')
def get_pending_transactions(request):
    transactions = SumUpCard.objects.filter(status=0)
    key = settings.SUMUP_AFFILIATE_KEY
    callback = settings.SUMUP_CALLBACK_HOSTNAME
    return render(request, 'pos/sumupcard.djhtml', {
        'transactions': transactions,
        'key': key,
        'url': callback
    })


def sumup_callback(request, tid):
    callback = request.GET
    tr = SumUpCard.objects.get(id=tid, status=1)
    if tr:
        if callback.get('smp-status') == 'failed':
            tr.status = 3
            tr.transaction_id = callback.get('smp-tx-code')
            tr.transaction_comment = callback.get('smp-message')
            tr.save()

        elif callback.get('smp-status') == 'success':
            api_key = SumUpAPIKey.objects.last()
            txstatus = fetch_transaction_status(api_key, callback.get('smp-tx-code'))
            if txstatus is True:
                tr.status = 2
                tr.transaction_id = callback.get('smp-tx-code')
                tr.transaction_comment = callback.get('smp-message')
                tr.save()
                tr.update_user()
    return HttpResponse('<script type="text/javascript">window.close()</script>')


# {"id":"88b907dd-a6ca-441f-b264-b3d02a8d1f79","status":"SUCCESSFUL","event_type":"CHECKOUT_STATUS_CHANGED"}
@csrf_exempt
def sumup_callbackonline(request, tid):
    callback = json.loads(request.body)
    checkoutid = callback['id']
    status = callback['status']

    try:
        tr = SumUpOnline.objects.get(id=tid, transaction_id=checkoutid, status=1)
    
    except:
        print('DEBUG: Id:' + str(tid) + ' CheckoutId:' + checkoutid + ' combo not found!')
        
    if status == 'SUCCESSFUL':
        api_key = SumUpAPIKey.objects.last()
        transactionstatus = fetch_onlinetransaction_status(api_key, checkoutid)
        if transactionstatus is True:
            print('transaction checked and OK')
            tr.status = 2
            tr.transaction_comment = status
            tr.save()
            tr.update_user()

        else:
            print('transaction could not be confirmed ' + checkoutid)
            tr.status = 3
            tr.transaction_comment = 'NOT CONFIRMED'
            tr.save()
    
    else:
        print('transaction failed')
        tr.status = 3
        tr.transaction_comment = status
        tr.save()

    return HttpResponse('OK')


def set_processing(request, transaction):
    tr = SumUpCard.objects.get(id=transaction)
    tr.status = 1
    tr.save()
    return HttpResponse('OK')


class SumUpAuthView(View):

    def dispatch(self, *args, **kwargs):
        self.action = kwargs.pop('action', None)
        self.instance_id = kwargs.get('instance_id', None)
        if not self.action:
            return HttpResponseBadRequest()
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        func = getattr(self, self.action, None)
        if not func:
            return HttpResponseBadRequest()
        return func(*args, **kwargs)

    def init(self, *args, **kwargs):
        instance = get_object_or_404(SumUpAPIKey, pk=self.instance_id)
        instance.access_code_state = uuid.uuid4()
        instance.save()
        data = {
            'response_type': 'code',
            'state': instance.access_code_state,
            'scope': 'transactions.history payments',
            'redirect_uri': urljoin(settings.SUMUP_CALLBACK_HOSTNAME, reverse('littleadmin:sumup_return')),
            'client_id': instance.client_id,
        }
        url = urljoin(API_URL, 'authorize') + '?' + urlencode(data)
        return redirect(url)

    def sumup_return(self, *args, **kwargs):
        code = self.request.GET['code']
        state = self.request.GET['state']
        instance = get_object_or_404(SumUpAPIKey, access_code_state=state)
        req = requests.post(
            url=urljoin(API_URL, 'token'),
            data={
                'grant_type': 'authorization_code',
                'client_id': instance.client_id,
                'client_secret': instance.client_secret,
                'code': code
            }
        )
        ret = req.json()
        instance.token = ret['access_token']
        instance.token_expiry = timezone.now() + timedelta(seconds=ret['expires_in'])
        instance.refresh_token = ret['refresh_token']
        instance.refresh_token_expiry = timezone.now() + timedelta(days=180)
        instance.save()
        return HttpResponse('OK')
