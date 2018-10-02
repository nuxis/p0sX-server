from django import forms

from .models.user import User


class CheckCreditForm(forms.Form):
    card = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'autofocus': 'autofocus'}))


class AddCreditForm(forms.Form):
    credit = forms.CharField(widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))


class ChangeCreditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['credit']
        widgets = {
            'credit': forms.NumberInput(attrs={'autofocus': 'autofocus'})
        }


class AddUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'card']
        widgets = {
            'card': forms.HiddenInput(),
            'first_name': forms.TextInput(attrs={'autofocus': 'autofocus'})
        }
