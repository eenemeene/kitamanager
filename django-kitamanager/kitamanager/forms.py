import datetime
from django import forms


class HistoryDateForm(forms.Form):
    """
    A form to change the date used to query data
    """

    historydate = forms.DateField(
        label="", initial=datetime.date.today, widget=forms.DateInput(attrs={"type": "date", "class": "col"})
    )


class EmployeeBonusPaymentForm(forms.Form):
    """
    A form to calculate a possible Employee Bonus payment
    """

    pay = forms.DecimalField(max_digits=10, decimal_places=2)
    year = forms.IntegerField(initial=datetime.date.today().year)
