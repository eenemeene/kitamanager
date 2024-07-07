from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django import forms
from kitamanager.models import EmployeeContract, Employee, EmployeePaymentPlan, EmployeePaymentTable
from kitamanager.forms import HistoryDateForm, EmployeeBonusPaymentForm, EmployeeCheckSagePayrollForm
from kitamanager.sage_payroll import SagePayrolls
from django.utils.translation import gettext_lazy as _
import datetime
from django.http import JsonResponse, HttpResponse
from kitamanager.definitions import CHART_COLORS, SALARY_EMPLOYER_ADDITION
from decimal import Decimal
from typing import Dict, List
import csv


@login_required
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


@login_required
def employee_list_csv(request):
    """
    list available Employee for the given historydate and return as CSV
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

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="employee-list-{historydate}.csv"'},
    )
    writer = csv.writer(response)
    # header row
    writer.writerow(
        [
            "ID",
            "First Name",
            "Last Name",
            "Begin date",
            "pay plan",
            "pay group",
            "pay level",
            "pay level next",
            "area",
            "qualification",
            "hours child per week",
            "hours management per week",
            "hours team per week",
            "hours misc per week",
            "monthly salary (Euro)",
        ]
    )
    for employee in EmployeeContract.objects.by_date(date=historydate):
        writer.writerow(
            [
                employee.person.pk,
                employee.person.first_name,
                employee.person.last_name,
                employee.person.begin_date,
                employee.pay_plan.name,
                employee.pay_group,
                employee.pay_level,
                employee.person.pay_level_next(historydate),
                employee.area.name,
                employee.qualification.name,
                employee.hours_child,
                employee.hours_management,
                employee.hours_team,
                employee.hours_misc,
                employee.person.salary(historydate),
            ]
        )
    return response


@login_required
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


@login_required
def employeepayment_detail(request, plan):
    """
    A list of EmployeePaymentTable for a given Plan
    """
    plan = get_object_or_404(EmployeePaymentPlan, name=plan)
    context = dict(
        plan=plan,
        object_list=EmployeePaymentTable.objects.select_related("plan").prefetch_related("entries").filter(plan=plan),
    )

    return render(
        request,
        "kitamanager/employeepayment_detail.html",
        context=context,
    )


@login_required
def employee_detail(request, pk):
    obj = get_object_or_404(Employee, pk=pk)
    return render(request, "kitamanager/employee_detail.html", {"object": obj})


@login_required
def employee_statistics(request):
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
        "kitamanager/employee_statistics.html",
        context=context,
    )


@login_required
def employee_bonuspayment(request):
    """
    Calculate a possible bonus payment for Employees
    """
    year = datetime.date.today().year
    pay = Decimal("1200")
    if request.method == "GET":
        form = EmployeeBonusPaymentForm(request.GET)
        if form.is_valid():
            year = form.cleaned_data["year"]
            pay = Decimal(form.cleaned_data["pay"])
        else:
            form = EmployeeBonusPaymentForm(initial={"year": year, "pay": pay})
    else:
        form = EmployeeBonusPaymentForm()
    # all employees with a contract at the end of the year
    d = datetime.date(year=year, month=12, day=31)
    data: Dict[str, List[Decimal]] = {}
    e_list = Employee.objects.by_date(d)
    # total pay for *all* employees
    pay_total_all = Decimal("0.0")
    for e in e_list:
        data[f"{e.last_name}, {e.first_name}"] = dict()
        data[f"{e.last_name}, {e.first_name}"]["by_month"] = []
        # pay for the current employee
        pay_total = Decimal("0.0")
        for hours in e.hours_by_month(year):
            pay_per_month = Decimal("0.0")
            if hours["hours"] > 0 and hours["hours_fulltime"] > 0:
                pay_per_month = pay / Decimal("12.0") * hours["hours"] / hours["hours_fulltime"]
                pay_total_all += pay_per_month
                pay_total += pay_per_month
            x = {
                "hours": hours["hours"],
                "hours_fulltime": hours["hours_fulltime"],
                "pay": pay_per_month,
            }
            data[f"{e.last_name}, {e.first_name}"]["by_month"].append(x)
        data[f"{e.last_name}, {e.first_name}"]["total"] = pay_total

    return render(
        request,
        "kitamanager/employee_bonuspayment.html",
        {"data": data, "year": year, "pay": pay, "pay_total_all": pay_total_all, "form": form},
    )


def _payrolls_data(payrolls):
    """
    build datastructure for data from payrolls and kitamanager
    """
    data = dict()
    # collect data for employees from kitamanager
    for employee in EmployeeContract.objects.by_date(payrolls.date):
        data[f"{employee.person.last_name}, {employee.person.first_name}"] = dict()
        data[f"{employee.person.last_name}, {employee.person.first_name}"]["kitamanager"] = {
            "hours": employee.hours_total,
            "pay_group": employee.pay_group,
            "pay_level": employee.pay_level,
        }
    # collect data for employees from payrolls
    for employee in payrolls.persons:
        d = data.get(f"{employee.last_name}, {employee.first_name}", {})
        d["payroll"] = {
            "hours": employee.hours,
            "pay_group": employee.pay_group,
            "pay_level": employee.pay_level,
        }
        data[f"{employee.last_name}, {employee.first_name}"] = d
    return data


@login_required
def employee_check_sage_payroll(request):
    """
    View to check a Sage Payroll
    """
    data = None
    payroll_date = None
    if request.method == "POST":
        form = EmployeeCheckSagePayrollForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data["file_pdf"]
            payrolls = SagePayrolls(f)
            data = _payrolls_data(payrolls)
            payroll_date = payrolls.date
    else:
        form = EmployeeCheckSagePayrollForm()

    return render(
        request,
        "kitamanager/employee_check_sage_payroll.html",
        {"form": form, "data": data, "payroll_date": payroll_date},
    )


@login_required
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


@login_required
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
