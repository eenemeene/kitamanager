import datetime
from django import forms
from kitamanager.models import Employee, EmployeeContract
from django.contrib.postgres.forms.ranges import DateRangeField


class HistoryDateForm(forms.Form):
    """
    A form to change the date used to query data
    """

    historydate = forms.DateField(
        label="", initial=datetime.date.today, widget=forms.DateInput(attrs={"type": "date", "class": "col"})
    )


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ("first_name", "last_name")


class EmployeeContractForm(forms.ModelForm):
    class Meta:
        model = EmployeeContract
        fields = (
            "date",
            "area",
            "qualification",
            "pay_plan",
            "pay_group",
            "pay_level",
            "hours_child",
            "hours_management",
            "hours_team",
            "hours_misc",
        )
