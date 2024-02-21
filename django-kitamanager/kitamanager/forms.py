import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from kitamanager.sage_payroll import SagePayrolls


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


def _validate_sage_payroll(value):
    try:
        SagePayrolls(value)
    except Exception:
        raise ValidationError(_(f"Can not read file {value}. This should be a PDF file. Wrong format?"))


class EmployeeCheckSagePayrollForm(forms.Form):
    """
    A Form to upload a .pdf (a Sage Payroll)that will be checked
    """

    file_pdf = forms.FileField(validators=[_validate_sage_payroll])
