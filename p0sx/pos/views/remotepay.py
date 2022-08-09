from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from pos.service.sumup import API_URL, create_checkout
from pos.models.sumup import SumUpAPIKey, SumUpOnline

from pos.forms import RemotePayForm
from pos.models.user import User


class RemotePayView(TemplateView):
    template_name = 'remotepay/pay.djhtml'


def pay(request):
    if request.method == 'POST':
        form = RemotePayForm(request.POST)

        if form.is_valid():
            phone = form.cleaned_data['phone']
            amount = form.cleaned_data['amount']
            # Check if user exists
            try:
                user = User.objects.get(phone=phone, is_crew=False)
            except User.DoesNotExist:
                return render(request, 'remotepay/pay.djhtml', {'form': form, 'error': True})

            # Assuming the user exists, we proceed
            t = SumUpOnline.objects.create(user=user, amount=amount)

            try:
                txid = create_checkout(SumUpAPIKey.objects.all().last(), t.id, t.amount, user.phone)
                t.transaction_id = txid
                t.status = 1
                t.save()
                return render(request, 'remotepay/process.djhtml', {'txid': txid, 'phone': phone, 'amount': amount})
            except:
                return render(request, 'remotepay/pay.djhtml', {'form': form, 'systemerror': True})

    else:
        form = RemotePayForm

    return render(request, 'remotepay/pay.djhtml', {'form': form})

def pay_callback(request, checkoutid):
    # Get the status of the transaction for the user
    t = SumUpOnline.objects.get(transaction_id=checkoutid)

    if (t.status == 0 or t.status == 3):
        return HttpResponseRedirect('/pay/error/')
    elif (t.status == 4):
        return HttpResponseRedirect('/pay/success/')
    elif (t.status == 1) or (t.status == 2):
        return render(request, 'remotepay/hold.djhtml', {'checkoutid': checkoutid})


def pay_success(request):
    return render(request, 'remotepay/success.djhtml')


def pay_error(request):
    return render(request, 'remotepay/error.djhtml')


def pay_hold(request):
    return render(request, 'remotepay/hold.djhtml')
