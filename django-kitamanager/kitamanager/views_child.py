import datetime
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from kitamanager.forms import HistoryDateForm
from kitamanager.models import Child, ChildContract, ChildPaymentPlan, ChildPaymentTable, RevenueEntry
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from kitamanager.definitions import CHART_COLORS, REVENUE_NAME_BERLIN


@login_required
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


@login_required
def child_list_future(request):
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
        object_list=Child.objects.future(historydate),
        historydate=historydate,
        form=form,
    )
    return render(
        request,
        "kitamanager/child_list_future.html",
        context=context,
    )


@login_required
def child_detail(request, pk):
    obj = get_object_or_404(Child, pk=pk)
    return render(request, "kitamanager/child_detail.html", {"object": obj})


@login_required
def child_statistics(request):
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
        historydate=historydate,
        form=form,
    )
    return render(
        request,
        "kitamanager/child_statistics.html",
        context=context,
    )


@login_required
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


@login_required
def childpayment_detail(request, plan):
    """
    A list of ChildPaymentTable for a given Plan
    """
    plan = get_object_or_404(ChildPaymentPlan, name=plan)
    context = dict(
        plan=plan,
        object_list=ChildPaymentTable.objects.select_related("plan").prefetch_related("entries").filter(plan=plan),
    )

    return render(
        request,
        "kitamanager/childpayment_detail.html",
        context=context,
    )


@login_required
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
            "title": _(f"Children grouped by area (on {historydate}"),
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


@login_required
def child_charts_count_by_month(request):
    """
    JSON response ChildContracts count at a given historydate for some years in the past
    and some years in the future
    Useful for charts
    """
    historydate = forms.DateField().clean(request.GET.get("historydate", datetime.date.today()))

    data = ChildContract.objects.count_by_month(
        historydate - relativedelta(years=3, month=1), historydate + relativedelta(years=2, month=12)
    )

    datasets = []
    month_labels = [
        _("January"),
        _("February"),
        _("March"),
        _("April"),
        _("May"),
        _("June"),
        _("July"),
        _("August"),
        _("September"),
        _("October"),
        _("November"),
        _("December"),
    ]
    for index, (year, val) in enumerate(data.items()):
        datasets.append(
            {
                "label": year,
                "data": val,
                "backgroundColor": CHART_COLORS[index],
            }
        )

    return JsonResponse(
        {
            "title": _("Children count by month"),
            "data": {"labels": month_labels, "datasets": datasets},
        }
    )


@login_required
def child_charts_pay_income_vs_invoice(request):
    """
    JSON response for comparing the calculated pay income for all children vs.
    the invoice received
    Useful for charts
    """
    historydate = forms.DateField().clean(request.GET.get("historydate", datetime.date.today()))
    dt_from = historydate - relativedelta(years=2, month=1)
    dt_to = historydate + relativedelta(years=1, month=6)

    invoice_name = REVENUE_NAME_BERLIN
    labels = []
    datasets = [
        {
            "label": _("calculated child payment (in €)"),
            "data": [],
            "backgroundColor": CHART_COLORS[0],
        },
        {
            "label": _("invoice %(invoice_name)s (in €)" % {"invoice_name": invoice_name}),
            "data": [],
            "backgroundColor": CHART_COLORS[1],
        },
    ]

    current = dt_from
    while current < dt_to:
        labels.append(current.strftime("%Y-%m"))
        datasets[0]["data"].append(ChildContract.objects.sum_payments(current))
        revenue_item = RevenueEntry.objects.by_date(current).filter(name=invoice_name).first()
        if revenue_item:
            datasets[1]["data"].append(revenue_item.pay)
        else:
            datasets[1]["data"].append(None)
        current = current + relativedelta(months=1)

    return JsonResponse(
        {
            "title": _("Calculated children payment vs. invoice"),
            "data": {"labels": labels, "datasets": datasets},
        }
    )
