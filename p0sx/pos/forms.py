from django import forms

from .models.user import User


class CheckCreditForm(forms.Form):
    card = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'autofocus': 'autofocus'}))


class AddCreditForm(forms.Form):
    credit = forms.CharField(widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))
    cash = forms.BooleanField(required=False)


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


class TimeFilterForm(forms.Form):
    from_time = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=False)
    to_time = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=False)


class RemotePayForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={'pattern': '[49]\d{7}', 'minlength': '8', 'maxlength': '8', 'oninvalid': 'this.setCustomValidity(\'Skriv inn et gyldig mobilnummer\')', 'oninput': 'this.setCustomValidity(\'\')'}))
    amount = forms.CharField(widget=forms.TextInput(attrs={'pattern': '(5[0-9]|[6-9][0-9]|[1-9][0-9]{2}|1000)', 'oninvalid': 'this.setCustomValidity(\'Skriv inn et beløp mellom kr. 50,- og kr. 1000,-\')', 'oninput': 'this.setCustomValidity(\'\')'}))
