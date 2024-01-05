import datetime
from django.http import HttpResponseRedirect
from django import forms
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from kitamanager.forms import HistoryDateForm
from kitamanager.models import Child, ChildContract, ChildPaymentPlan, ChildPaymentTable
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from kitamanager.definitions import CHART_COLORS


def child_list(request):
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
        object_list=ChildContract.objects.by_date(historydate),
        sum_payments=ChildContract.objects.sum_payments(date=historydate),
        historydate=historydate,
        form=form,
    )
    return render(
        request,
        "kitamanager/child_list.html",
        context=context,
    )


def child_detail(request, pk):
    obj = get_object_or_404(Child, pk=pk)
    return render(request, "kitamanager/child_detail.html", {"object": obj})


def childpayment_list(request):
    """
    A list of ChildPaymentPlan's
    """
    context = dict(
        object_list=ChildPaymentPlan.objects.all(),
    )
    return render(
        request,
        "kitamanager/childpayment_list.html",
        context=context,
    )


def childpayment_detail(request, plan):
    """
    A list of ChildPaymentTable for a given Plan
    """
    plan = get_object_or_404(ChildPaymentPlan, name=plan)
    context = dict(
        plan=plan,
        object_list=ChildPaymentTable.objects.select_related("plan")
        .prefetch_related("entries")
        .filter(plan=plan)
        .order_by("-date"),
    )

    return render(
        request,
        "kitamanager/childpayment_detail.html",
        context=context,
    )


def child_charts_count_group_by_area(request):
    """
    JSON response ChildContracts count at a given historydate grouped by area
    Useful for charts
    """
    historydate = forms.DateField().clean(request.GET.get("historydate", datetime.date.today()))

    grouped_areas = ChildContract.objects.count_group_by_area(historydate)
    labels = []
    values = []
    for g in grouped_areas:
        labels.append(g["area"])
        values.append(g["total"])

    return JsonResponse(
        {
            "title": _(f"Childreen grouped by area (on {historydate}"),
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": _("Count"),
                        "backgroundColor": CHART_COLORS[0 : len(labels)],
                        "data": values,
                    }
                ],
            },
        }
    )
