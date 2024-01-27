import datetime
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.translation import gettext_lazy as _
from kitamanager.models import ChildContract, EmployeeContract
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from kitamanager.definitions import CHART_COLORS


@login_required
def statistic_charts_child_requirement_vs_employee_hours(request):
    """
    JSON response for comparing the required hours for children with the
    available working hours from employees
    Useful for charts
    """
    historydate = forms.DateField().clean(request.GET.get("historydate", datetime.date.today()))
    dt_from = historydate - relativedelta(years=1)
    dt_to = historydate + relativedelta(months=6)

    labels = []
    datasets = [
        {
            "label": _("requirements from children (in h/week)"),
            "data": [],
            "backgroundColor": CHART_COLORS[0],
        },
        {
            "label": _("employee child+team working hours (in h/week)"),
            "data": [],
            "backgroundColor": CHART_COLORS[1],
        },
    ]

    current = dt_from
    while current < dt_to:
        labels.append(current.strftime("%Y-%m"))
        # children requirements
        sum_requirements, sum_requirements_hours_per_week = ChildContract.objects.sum_requirements(current)
        datasets[0]["data"].append(sum_requirements_hours_per_week)
        # employee working hours (child and team hours only)
        sum_hours = EmployeeContract.objects.sum_hours(current)
        datasets[1]["data"].append(sum_hours["hours_child_sum"] + sum_hours["hours_team_sum"])
        current = current + relativedelta(months=1)

    return JsonResponse(
        {
            "title": _("Children requirements vs. Employee working hours"),
            "data": {"labels": labels, "datasets": datasets},
        }
    )
