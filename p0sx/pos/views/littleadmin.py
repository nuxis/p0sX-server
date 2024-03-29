import csv
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Case, IntegerField, Sum, When, Max, Min
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ..forms import AddCreditForm, AddUserForm, ChangeCreditForm, CheckCreditForm, TimeFilterForm
from ..ge_importer import GeekEventsImporter
from ..models.shift import Shift
from ..models.stock import Item, Order, OrderLine
from ..models.sumup import SumUpAPIKey, SumUpCard, SumUpTransaction
from ..models.user import CreditUpdate, GeekeventsToken, User
from ..serializers.shift import ShiftSerializer

from pos.service.ge_sso import get_user


def check_credit(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']
            user = User.objects.filter(card__iexact=card)

            if not user:
                return HttpResponseRedirect(reverse_lazy('littleadmin:check'))

            orders = Order.objects.filter(user_id=user[0].id).order_by('-date')[0:3]

            return render(request, 'pos/credit_check.djhtml', {
                'form': CheckCreditForm(),
                'orders': get_order_details(orders),
                'table': True,
                'used': user[0].used,
                'credit': user[0].credit,
                'left': user[0].left
            })
        else:
            return HttpResponseRedirect(reverse_lazy('littleadmin:check'))
    else:
        return render(request, 'pos/credit_check.djhtml', {
            'form': CheckCreditForm(),
            'table': False,
        })


def get_order_details(orders):
    value = "<ul>\n"
    for order in orders:
        value += f"<li><b>{order.info}</b>\n"
        value += "<ul style='margin-left: 15px'>\n"

        for line in order.orderlines.all():
            value += f"<li>{line}</li>\n"
        value += "</ul>\n"
    value += "</ul>\n"
    return value


@login_required
def credit_overview(request):
    bought = OrderLine.objects.all().exclude(order__user__isnull=True).values('order__user').annotate(used=Sum('price'))
    users = User.objects.all().values()
    for user in users:
        for b in bought:
            user['used'] = 0
            user['left'] = 0
            if b['order__user'] == user['id']:
                user['used'] = b['used']
                user['left'] = user['credit'] - user['used']
                break

    context = {
        'users': users
    }

    return render(request, 'pos/credit_overview.djhtml', context)


@login_required
def crew_report(request):
    crew = User.objects.filter(is_crew=True)

    credit_result = []
    for c in crew:
        items = OrderLine.objects.filter(order__user=c).values('item__name')\
            .annotate(total=Sum('price'),
                      number=Sum(Case(When(price__gt=0, then=1), default=-1, output_field=IntegerField())))

        total = sum(map(lambda x: x['total'], items))
        credit_result.append({'card': c.card, 'lines': items, 'name': c.first_name + ' ' + c.last_name, 'total': total})

    return render(request, 'pos/crew_report.djhtml', {'crew': credit_result})


@login_required
def credit_edit(request, card=None):
    if request.POST:
        form = ChangeCreditForm(request.POST)
        if form.is_valid():
            credit = form.cleaned_data['credit']
            user = get_object_or_404(User, card__iexact=card)

            user.credit = credit
            user.save()
            return HttpResponseRedirect(reverse_lazy('littleadmin:overview'))
    else:
        user = get_object_or_404(User, card__iexact=card)
        form = ChangeCreditForm(instance=user)

        return render(request, 'pos/credit_edit.djhtml', {'form': form, 'target': user})


@login_required
def sale_overview_csv(request):
    from_time = None
    to_time = None

    if request.POST:
        form = TimeFilterForm(request.POST)
        if form.is_valid():
            from_time = form.cleaned_data['from_time']
            to_time = form.cleaned_data['to_time']
    else:
        form = TimeFilterForm()

    order_lines = OrderLine.objects.all().values('item__id', 'order__payment_method')
    if from_time is not None and to_time is not None:
        order_lines = order_lines.filter(order__date__gte=from_time).filter(order__date__lt=to_time)
    order_lines = order_lines.annotate(total=Sum('price'),
                  first_sold=Min('order__date'),
                  last_sold=Max('order__date'),
                  sold=Sum(Case(When(price__gte=0, then=1), default=-1, output_field=IntegerField())))

    items = Item.objects.all().values('name', 'category__name', 'id', 'price')

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="sale_overview.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["Category", "Name", "First sold", "Last sold", "Prepaid", "Credit", "Sold"])
    for item in items:
        per_payment_method = order_lines.filter(item_id=item['id'])
        first_sold = per_payment_method.aggregate(Min('first_sold'))['first_sold__min']
        last_sold = per_payment_method.aggregate(Max('last_sold'))['last_sold__max']
        try:
            credit = per_payment_method.filter(order__payment_method=1)[0]
        except IndexError:
            credit = {'sold': 0, 'total': 0, 'first_sold': None, 'last_sold': None}
        try:
            prepaid = per_payment_method.filter(order__payment_method=4)[0]
        except IndexError:
            prepaid = {'sold': 0, 'total': 0, 'first_sold': None, 'last_sold': None}

        writer.writerow([item['category__name'], item['name'], first_sold, last_sold, prepaid['total'], credit['total'], prepaid['sold'] + credit['sold']])

    return response

@login_required
def sale_overview(request):
    from_time = None
    to_time = None

    if request.POST:
        form = TimeFilterForm(request.POST)
        if form.is_valid():
            from_time = form.cleaned_data['from_time']
            to_time = form.cleaned_data['to_time']
    else:
        form = TimeFilterForm()

    order_lines = OrderLine.objects.all().values('item__id', 'order__payment_method')
    if from_time is not None and to_time is not None:
        order_lines = order_lines.filter(order__date__gte=from_time).filter(order__date__lt=to_time)
    order_lines = order_lines.annotate(total=Sum('price'),
                  first_sold=Min('order__date'),
                  last_sold=Max('order__date'),
                  sold=Sum(Case(When(price__gte=0, then=1), default=-1, output_field=IntegerField())))

    items = Item.objects.all().values('name', 'category__name', 'id', 'price')
    total = {'prepaid': 0, 'credit': 0, 'total': 0}

    overview = {}

    for item in items:
        per_payment_method = order_lines.filter(item_id=item['id'])
        first_sold = per_payment_method.aggregate(Min('first_sold'))['first_sold__min']
        last_sold = per_payment_method.aggregate(Max('last_sold'))['last_sold__max']
        try:
            credit = per_payment_method.filter(order__payment_method=1)[0]
        except IndexError:
            credit = {'sold': 0, 'total': 0, 'first_sold': None, 'last_sold': None}
        try:
            prepaid = per_payment_method.filter(order__payment_method=4)[0]
        except IndexError:
            prepaid = {'sold': 0, 'total': 0, 'first_sold': None, 'last_sold': None}

        item['first_sold'] = first_sold
        item['last_sold'] = last_sold
        item['prepaid'] = prepaid['total']
        item['credit'] = credit['total']
        item['sold'] = prepaid['sold'] + credit['sold']
        item['total'] = item['prepaid'] + item['credit']

        if item['price'] < 0:
            item['sold'] *= -1

        if item['category__name'] in overview.keys():
            overview[item['category__name']].append(item)
        else:
            overview[item['category__name']] = [item]

        total['prepaid'] += item['prepaid']
        total['credit'] += item['credit']
        total['total'] += item['total']

    category_totals = []

    for category_name, category_items in overview.items():
        category_total = {}
        category_total['name'] = "Total"
        category_total['prepaid'] = 0
        category_total['credit'] = 0
        category_total['sold'] = 0
        category_total['total'] = 0
        for category_item in category_items:
            print(category_item)
            category_total['prepaid'] = category_total['prepaid'] + category_item['prepaid']
            category_total['credit'] = category_total['credit'] + category_item['credit']
            category_total['sold'] = category_total['sold'] + category_item['sold']
            category_total['total'] = category_total['total'] + category_item['total']
        category_items.append(category_total)
        
        category_total_copy = category_total.copy();
        category_total_copy['name'] = category_name
        category_totals.append(category_total_copy)

    shifts = ShiftSerializer(Shift.objects.all(), many=True)
    return render(request, 'pos/sale_overview.djhtml', {'overview': overview, 'categories': category_totals, 'shifts': shifts.data, 'total': total, 'form': form})


@permission_required("pos.update_credit")
def scan_user_card(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']

            user = User.objects.filter(card__iexact=card)

            if not user:
                return redirect('littleadmin:add_user', card=card)

            return redirect('littleadmin:add_user_credit', card=card)
        else:
            return HttpResponseRedirect(reverse_lazy('littleadmin:scan_user_card'))
    else:
        return render(request, 'pos/scan_card.djhtml', {
            'form': CheckCreditForm(),
            'table': False,
        })


@permission_required('pos.import_credit')
def fetch_credit_from_ge(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Failed to verify, are you crew?")
            return render(request, 'pos/import_geekevents.djhtml', {'items': [], 'form': CheckCreditForm()})

        verify_user = form.cleaned_data['card']

        crew = User.objects.filter(card__iexact=verify_user)

        if not crew or not crew[0].is_crew:
            messages.error(request, "Failed to verify, are you crew?")
            return render(request, 'pos/import_geekevents.djhtml', {'items': [], 'form': CheckCreditForm()})

        importer = GeekEventsImporter(settings.GEEKEVENTS_TOKEN, settings.GEEKEVENTS_ITEM_ID)
        items = []
        try:
            items = importer.get_unfetched_items()
        except:
            messages.error(request, f"Failed to get list of items from GeekEvents")
            return render(request, 'pos/import_geekevents.djhtml', {'items': [], 'form': CheckCreditForm()})

        for item in items:
            try:
                existing_order = CreditUpdate.objects.filter(geekevents_id=item.order_id)
                if existing_order and len(existing_order) > 0:
                    importer.mark_as_fetched(item.item_id)
                    continue

                with transaction.atomic():
                    users = User.objects.filter(card__iexact=item.badge)
                    user = None
                    if not users or len(users) != 1:
                        user = User.create(item.badge, item.amount, item.first_name, item.last_name, '', '')
                    else:
                        user = users[0]
                        user.credit += item.amount

                    user.save()

                    update = CreditUpdate.create(user, crew[0], item.amount, item.order_id)
                    update.save()

                    success = importer.mark_as_fetched(item.item_id)
                    if not success:
                        transaction.rollback()
                        messages.error(request, f"Failed to mark the item as fetched for user {item.first_name} {item.last_name}")
                        continue

                messages.success(request, f"Imported {item.amount},- for {item.first_name} {item.last_name}")
            except:
                messages.error(request, f"Failed to mark the item as fetched for user {item.first_name} {item.last_name}")

        return render(request, 'pos/import_geekevents.djhtml', {'items': items, 'form': CheckCreditForm()})
    else:
        return render(request, 'pos/import_geekevents.djhtml', {'items': [], 'form': CheckCreditForm()})


@permission_required('pos.update_credit')
def add_user_credit(request, card=None):
    if request.POST:
        form = AddCreditForm(request.POST)

        if form.is_valid():
            credit = form.cleaned_data['credit']
            cash = form.cleaned_data['cash']
            user = get_object_or_404(User, card__iexact=card)

            if user.is_crew:
                messages.error(request, "You cannot change the credit of Crew")
                return redirect('littleadmin:scan_user_card')

            try:
                amount = int(credit)
            except ValueError:
                return redirect('littleadmin:add_user_credit', card)

            if amount > 1000:
                messages.error(request, "The maximum credit that can be added at once is 1000. Add multiple times if more is needed")
                return redirect('littleadmin:add_user_credit', card)

            if(cash):
                return redirect('littleadmin:verify_add_credit_cash', user.id, amount)


            transaction = SumUpCard.objects.create(user=user, amount=amount, authorized_user=request.user)
            tid = transaction.id

            return redirect('littleadmin:verify_add_credit', tid)
        else:
            return redirect('littleadmin:add_user_credit', card)
    else:
        user = get_object_or_404(User, card__iexact=card)

        if user.is_crew:
            messages.error(request, "You cannot change the credit of Crew")
            return redirect('littleadmin:scan_user_card')

        form = AddCreditForm()
        sumup_url = reverse('littleadmin:add_user_credit_sumup', kwargs={'card': card})
        return render(request, 'pos/add_credit.djhtml', {'form': form, 'target': user, 'sumup_url': sumup_url})


def check_sumup_status(request, tid):
    obj = SumUpCard.objects.get(pk=tid)
    return HttpResponse(obj.status)


class AddUserSumupCredit(TemplateView):
    UPDATE_SECONDS = 300

    template_name = 'pos/add_credit_sumup.djhtml'
    transaction = None
    user = None

    @method_decorator(login_required)
    @method_decorator(permission_required('pos.update_credit'))
    def dispatch(self, *args, **kwargs):
        self.user = get_object_or_404(User, card__iexact=kwargs.get('card', None))
        self.transaction = SumUpTransaction.objects.all().filter(handled=False, pk=kwargs.get('transaction_id',
                                                                                              0)).first()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        for key in SumUpAPIKey.objects.all():
            key.get_unhandled_transactions(self.UPDATE_SECONDS)
        context['available'] = SumUpTransaction.objects.all().filter(
            timestamp__gte=timezone.now() - datetime.timedelta(seconds=self.UPDATE_SECONDS),
            status='SUCCESSFUL', handled=False
        )
        context['seconds'] = self.UPDATE_SECONDS
        context['url'] = self.request.path
        context['form'] = CheckCreditForm()
        context['trans'] = self.transaction
        return context

    def get(self, *args, **kwargs):
        if kwargs.get('verify', None):
            self.template_name = 'pos/add_credit_sumup_confirm.djhtml'
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if not self.transaction:
            # Crewmember must input badge ID
            self.transaction = get_object_or_404(
                SumUpTransaction,
                pk=self.request.POST.get('transaction_id', None),
                handled=False
            )
            return HttpResponse(reverse('littleadmin:add_user_credit_sumup_verify', kwargs={
                'card': self.user.card,
                'transaction_id': self.transaction.pk,
            }))
        self.crew_badge_id = self.request.POST.get('card', None)
        self.crew_member = get_object_or_404(User, card__iexact=self.crew_badge_id)
        self.transaction.use_on_user(self.user, self.crew_member)
        messages.success(self.request, f"Success! Credit set to {self.user.left}")
        return redirect('littleadmin:scan_user_card')


@permission_required('pos.update_credit')
def add_user(request, card=None):
    if request.POST:
        form = AddUserForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            user = User.create(card, 0, first_name, last_name, '', '')

            user.save()
            return redirect('littleadmin:scan_user_card')
        else:
            messages.error(request, "Failed to add user")
            return HttpResponseRedirect(reverse_lazy('littleadmin:add_user'))
    else:
        form = AddUserForm(initial={'card': card})
        return render(request, 'pos/add_user.djhtml', {
            'form': form
        })


@permission_required('pos.update_credit')
def verify_add_credit(request, tid=''):

    transaction = SumUpCard.objects.get(pk=tid)
    if transaction.status == 4:
        messages.success(request, str(transaction.amount) + ' added to ' + str(transaction.user))
        return HttpResponseRedirect(reverse_lazy('littleadmin:check'))

    if transaction.status == 3:
        messages.error(request, 'Transaction failed')
        return HttpResponseRedirect(reverse_lazy('littleadmin:scan_user_card'))

    else:
        return render(request, 'pos/verify_add_credit.djhtml', {
            'tid': tid,
            'status': transaction.get_status_display()
        })


@permission_required('pos.update_credit')
def verify_add_credit_cash(request, user='', amount=''):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            target = get_object_or_404(User, id=int(user))
            card = form.cleaned_data['card']
            crew = User.objects.filter(card__iexact=card)

            if not crew or not crew[0].is_crew:
                messages.error(request, "Failed to verify, are you crew?")
                return redirect('littleadmin:verify_add_credit_cash', user, amount)

            target.credit += int(amount)
            target.save()

            update = CreditUpdate.create(target, crew[0], amount)
            update.save()

            messages.success(request, f"Success! Credit set to {target.left}")
            return redirect('littleadmin:scan_user_card')
        else:
            messages.error(request, "Failed to add user")
            return HttpResponseRedirect(reverse_lazy('littleadmin:scan_user_card'))
    else:
        form = CheckCreditForm()
        return render(request, 'pos/verify_add_credit_cash.djhtml', {
            'form': form
        })


def group_credit_updates(date, group_by):
    times = [
        datetime.timedelta(hours=0),
        datetime.timedelta(hours=6),
        datetime.timedelta(hours=12),
        datetime.timedelta(hours=18)
    ]
    seconds = (date.hour * 60 * 60) + (date.minute * 60) + date.second
    seconds /= group_by.total_seconds()

    index = int(seconds)

    timestamp = datetime.datetime.combine(date.date(), datetime.datetime.min.time()) + times[index]

    return timestamp


@login_required()
def add_credit_stats(request):
    if request.POST:
        form = TimeFilterForm(request.POST)
        if not form.is_valid():
            return redirect('littleadmin:add_credit_stats')

        from_time = form.cleaned_data['from_time']
        to_time = form.cleaned_data['to_time']

        updates = CreditUpdate.objects.filter(timestamp__lte=to_time, timestamp__gte=from_time)
        orders = Order.objects.filter(date__lte=to_time, date__gte=from_time)

        total_out = sum([x.sum for x in orders])

        total = sum([x.amount for x in updates])

        form = TimeFilterForm(initial={'from_time': f"{from_time:%Y-%m-%dT%H:%M}", 'to_time': f"{to_time:%Y-%m-%dT%H:%M}"})
    else:
        total = 0
        total_out = 0
        updates = []
        orders = []
        form = TimeFilterForm()

    return render(request, 'pos/add_credit_stats.djhtml', {
        'updates': updates,
        'orders': orders,
        'total': total,
        'total_out': total_out,
        'form': form
    })

@login_required()
def update_ge_user(request):
    ge_id = request.GET.get('id', None)
    if ge_id is not None:
        user = GeekeventsToken.objects.get(ge_user_id=ge_id)
        if not user:
            return;
        ge_user = get_user(user.ge_user_id, user.timestamp, user.token)
        user.user.card = ge_user['usercard'].split('||')[0]
        user.user.first_name = ge_user['first_name']
        user.user.last_name = ge_user['last_name']
        user.user.phone = ge_user['phone']
        user.user.email = ge_user['email']
        user.user.save()
        return redirect('/littleadmin/update_ge_user')

    users = GeekeventsToken.objects.all();

    return render(request, 'pos/update_ge_user.djhtml', {
        'users': users
    })
