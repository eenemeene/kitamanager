from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django import forms
from kitamanager.models import EmployeeContract, Employee, EmployeePaymentPlan, EmployeePaymentTable
from kitamanager.forms import HistoryDateForm, EmployeeContractForm
from django.views.generic import ListView, UpdateView, CreateView, DetailView, FormView
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from dateutil.parser import parse
import datetime
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from kitamanager.definitions import CHART_COLORS, SALARY_EMPLOYER_ADDITION
from decimal import Decimal


def employee_list(request):
    """
    list available Employee for the given historydate
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

    sum_salaries = EmployeeContract.objects.sum_salaries(date=historydate)
    sum_salaries_plus_employer_addition = sum_salaries + sum_salaries * Decimal(f"{SALARY_EMPLOYER_ADDITION}")
    context = dict(
        object_list=EmployeeContract.objects.by_date(date=historydate),
        sum_hours=EmployeeContract.objects.sum_hours(date=historydate),
        sum_salaries=sum_salaries,
        sum_salaries_plus_employer_addition=sum_salaries_plus_employer_addition,
        salary_employer_addition=Decimal(f"{SALARY_EMPLOYER_ADDITION}") * Decimal("100.0"),
        historydate=historydate,
        form=form,
    )

    return render(
        request,
        "kitamanager/employee_list.html",
        context=context,
    )


def employeepayment_list(request):
    """
    A list of EmployeePaymentPlan's
    """
    context = dict(
        object_list=EmployeePaymentPlan.objects.all(),
    )
    return render(
        request,
        "kitamanager/employeepayment_list.html",
        context=context,
    )


def employeepayment_detail(request, plan):
    """
    A list of EmployeePaymentTable for a given Plan
    """
    plan = get_object_or_404(EmployeePaymentPlan, name=plan)
    context = dict(
        plan=plan,
        object_list=EmployeePaymentTable.objects.select_related("plan")
        .prefetch_related("entries")
        .filter(plan=plan)
        .order_by("-date"),
    )

    return render(
        request,
        "kitamanager/employeepayment_detail.html",
        context=context,
    )


class EmployeeDetailView(DetailView):
    model = Employee
    template_name = "kitamanager/employee_detail.html"
    fields = ["date", "area", "qualification", "hours_child", "hours_management", "hours_team", "hours_misc"]


def employee_charts_count_group_by_area(request):
    """
    JSON response EmployeeContracts count at a given historydate grouped by area
    Useful for charts
    """
    historydate = forms.DateField().clean(request.GET.get("historydate", datetime.date.today()))

    grouped_areas = EmployeeContract.objects.count_group_by_area(historydate)
    labels = []
    values = []
    for g in grouped_areas:
        labels.append(g["area"])
        values.append(g["total"])

    return JsonResponse(
        {
            "title": _(f"Employees grouped by area (on {historydate}"),
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


def employee_charts_hours_group_by_area(request):
    """
    JSON response EmployeeContract hours at a given historydate grouped by are
    Useful for charts
    """
    historydate = forms.DateField().clean(request.GET.get("historydate", datetime.date.today()))

    grouped_areas = EmployeeContract.objects.sum_hours_group_by_area(historydate)
    labels = []
    values = []
    for g in grouped_areas:
        labels.append(g["area"])
        values.append(g["hours_sum"])

    return JsonResponse(
        {
            "title": _(f"Employee working hours grouped by area (on {historydate}"),
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
