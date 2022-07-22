from django.http.response import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

from ..models.user import GeekeventsToken, User

from django.conf import settings

from pos.service.ge_sso import get_user, validate_token, user_has_ticket

def add_user(request):
    callback_url = 'https://' + request.get_host() + '/sso/add_user_callback'
    return render(request, 'sso/add_user.djhtml', {'callback_url': callback_url})

def add_user_callback(request):
    if not request.GET:
        return HttpResponseBadRequest("Only GET requests allowed")

    token = request.GET.get('token', None)
    user_id = request.GET.get('id', None)
    timestamp = request.GET.get('timestamp', None)
    if not token:
        return HttpResponseBadRequest("Could not find 'token' query parameter")
    if not user_id:
        return HttpResponseBadRequest("Could not find 'user_id' query parameter")
    if not timestamp:
        return HttpResponseBadRequest("Could not find 'timestamp' query parameter")

    user_query = GeekeventsToken.objects.filter(ge_user_id = user_id)
    if len(user_query) != 0:
        return HttpResponseBadRequest("Your user already exists")

    if not validate_token(user_id, timestamp, token):
        return HttpResponseBadRequest("The token returned from Geekevents could not be validated")

    if not user_has_ticket(user_id, timestamp, token):
        return HttpResponseForbidden("You do not have a valid ticket to this event")

    try:
        ge_user = get_user(user_id, timestamp, token)
    except:
        return HttpResponseBadRequest("Failed to get user details from Geekevents")

    card_string = ge_user['usercard']
    if type(card_string) != str or not '||' in card_string:
        return HttpResponseBadRequest("You do not have a badge number on your user, are you correctly registered?")

    card = card_string.split('||')[0]
    first_name = ge_user['first_name']
    last_name = ge_user['last_name']
    phone = ge_user['phone']
    email = ge_user['email']

    card_query = User.objects.filter(card=card)
    if len(card_query) != 0:
        return HttpResponseBadRequest("A user with your ID is already registered")

    user = User.create(card, 0, first_name, last_name, phone, email)
    user.save()
    user_token = GeekeventsToken.create(user_id, timestamp, token, user)
    user_token.save()

    redirect_url = settings.GE_SSO_SUCCESS_REDIRECT
    if redirect_url is not None:
        return redirect(redirect_url)
    return render(request, 'sso/added_user.djhtml', {'first_name': first_name, 'last_name': last_name})
