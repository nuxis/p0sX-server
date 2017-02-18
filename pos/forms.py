from django import forms

from .models.crew import Crew


class CheckCreditForm(forms.Form):
    card = forms.CharField(100)


class ChangeCreditForm(forms.ModelForm):

    class Meta:
        model = Crew
        fields = ['credit']
