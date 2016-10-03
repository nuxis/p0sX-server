from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from ..forms import ChangeCreditForm, CheckCreditForm
from ..models.crew import Crew


def check_credit(request):
    if request.POST:
        form = CheckCreditForm(request.POST)

        if form.is_valid():
            card = form.cleaned_data['card']

            crew = get_object_or_404(Crew, card=card)

            print(crew)
            print(crew.used)
            print(crew.credit)
            print(crew.left)

            return render(request, 'pos/credit_check.djhtml', {
                'form': CheckCreditForm(),
                'table': True,
                'used': crew.used,
                'credit': crew.credit,
                'left': crew.left
            })
    else:
        return render(request, 'pos/check.djhtml', {
            'form': CheckCreditForm(),
            'table': False,
        })


@login_required
def credit_overview(request):
    crew_list = Crew.objects.all()

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
