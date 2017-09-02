from django import forms

from .models.user import User


class CheckCreditForm(forms.Form):
    card = forms.CharField(max_length=100, widget=forms.PasswordInput())


class ChangeCreditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['credit']
