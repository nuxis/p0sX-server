from django import forms

from .models.user import User


class CheckCreditForm(forms.Form):
    card = forms.CharField(max_length=100, widget=forms.PasswordInput())


class ChangeCreditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['credit']


class AddUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email', 'credit', 'card']
        widgets = {
            'card': forms.PasswordInput(render_value=True),
            'first_name': forms.TextInput(attrs={'autofocus': 'autofocus'})
        }
