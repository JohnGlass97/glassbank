from django import forms


class RedeemForm(forms.Form):
    code = forms.CharField(label='Code', min_length=0, max_length=8)
