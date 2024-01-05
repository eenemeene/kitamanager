import datetime
from django.http import HttpResponseRedirect
from django import forms
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.shortcuts import render
from kitamanager.forms import HistoryDateForm
from kitamanager.forms_bank import BankAccountImportForm
from kitamanager.models import BankAccount, BankAccountEntry
from kitamanager.bankimport import BankAccountEntryImport
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from kitamanager.definitions import CHART_COLORS
from django.contrib.auth.decorators import login_required


@login_required
def bankaccount_list(request):
    """
    list available BankAccount for the given historydate
    """
    historydate = datetime.date.today()
    if request.method == "GET":
        form = HistoryDateForm(request.GET)
        if form.is_valid():
            historydate = form.cleaned_data["historydate"]
        else:
            form = HistoryDateForm(initial={"historydate": historydate.strftime("%Y-%m-%d")})
    else:
        form = HistoryDateForm()

    context = dict(
        object_list=BankAccountEntry.objects.by_date(historydate),
        historydate=historydate,
        form=form,
    )
    return render(
        request,
        "kitamanager/bankaccount_list.html",
        context=context,
    )


@login_required
def bankaccount_charts_sum_balance_by_month(request):
    """
    JSON response of BankAccountEntry with monthly values
    Useful for charts
    """
    historydate = forms.DateField().clean(request.GET.get("historydate", datetime.date.today()))

    data = BankAccountEntry.objects.sum_balance_by_month(
        date_start=historydate - relativedelta(months=15), date_end=historydate + relativedelta(months=3)
    )
    labels = []
    values = []

    for label, value in sorted(data.items()):
        labels.append(label.strftime("%Y-%m"))
        values.append(value)

    return JsonResponse(
        {
            "title": _(f"monthly bank account balance sum in € (on {historydate})"),
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": _("Balance (in €) over time"),
                        "backgroundColor": CHART_COLORS[0],
                        "data": values,
                    }
                ],
            },
        }
    )
