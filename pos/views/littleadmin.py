from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from ..forms import ChangeCreditForm, CheckCreditForm
from ..models.crew import Crew
from ..models.stock import OrderLine


def check_credit(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']

            crew = Crew.objects.filter(card=card)

            if not crew:
                return HttpResponseRedirect(reverse_lazy('littleadmin:check'))

            return render(request, 'pos/credit_check.djhtml', {
                'form': CheckCreditForm(),
                'table': True,
                'used': crew[0].used,
                'credit': crew[0].credit,
                'left': crew[0].left
            })
        else:
            return HttpResponseRedirect(reverse_lazy('littleadmin:check'))
    else:
        return render(request, 'pos/credit_check.djhtml', {
            'form': CheckCreditForm(),
            'table': False,
        })


@login_required
def credit_overview(request):
    crew_list = Crew.objects.all().order_by('last_name', 'first_name')

    context = {
        'crew_list': crew_list
    }

    return render(request, 'pos/credit_overview.djhtml', context)


@login_required
def credit_edit(request, card=None):
    if request.POST:
        form = ChangeCreditForm(request.POST)
        if form.is_valid():
            credit = form.cleaned_data['credit']
            crew = get_object_or_404(Crew, card=card)

            crew.credit = credit
            crew.save()
            return HttpResponseRedirect(reverse_lazy('littleadmin:overview'))
    else:
        crew = get_object_or_404(Crew, card=card)
        form = ChangeCreditForm(instance=crew)

        return render(request, 'pos/credit_edit.djhtml', {'form': form, 'crew': crew})


@login_required
def sale_overview(request):
    order_lines = OrderLine.objects.all()

    overview = {}
    for order_line in order_lines:
        if order_line.item in overview.keys():
            overview[order_line.item]['price'] += order_line.price
            overview[order_line.item]['sum'] += 1
        else:
            overview[order_line.item] = {}
            overview[order_line.item]['price'] = order_line.price
            overview[order_line.item]['sum'] = 1

    splitted_by_category = {}
    for item, acc in overview.items():
        if item.category in splitted_by_category.keys():
            splitted_by_category[item.category].append((item, acc))
        else:
            splitted_by_category[item.category] = [(item, acc)]

    return render(request, 'pos/sale_overview.djhtml', {'category_with_items': splitted_by_category})
