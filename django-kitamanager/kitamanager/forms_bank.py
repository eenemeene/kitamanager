from django import forms


class BankAccountImportForm(forms.Form):
    file = forms.FileField()
