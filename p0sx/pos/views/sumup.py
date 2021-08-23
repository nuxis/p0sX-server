import uuid
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls.base import reverse_lazy
import requests
from datetime import timedelta, datetime
from urllib.parse import urljoin, urlencode

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from pos.models.sumup import SumUpAPIKey, SumUpCard
from pos.service.sumup import API_URL

def get_pending_transactions(request):
    transactions = SumUpCard.objects.filter(status=0)
    return render(request, 'pos/sumupcard.djhtml', {
        'transactions': transactions
    })

def sumup_callback(request, tid):
    callback = request.GET
    tr = SumUpCard.objects.get(id=tid)
    if callback.get('smp-status') == 'failed':
        tr.status = 3
        tr.transaction_id = callback.get('smp-tx-code')
        tr.transaction_comment = callback.get('smp-message')
        tr.save()
        tr.update_user()

    elif callback.get('smp-status') == 'success':
        tr.status = 2
        tr.transaction_id = callback.get('smp-tx-code')
        tr.transaction_comment = callback.get('smp-message')
        tr.save()
        tr.update_user()

    return HttpResponse('<script type="text/javascript">window.close()</script>')

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
            'scope': 'transactions.history',
            'redirect_uri': urljoin(settings.SITE_URL, reverse('littleadmin:sumup_return')),
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
