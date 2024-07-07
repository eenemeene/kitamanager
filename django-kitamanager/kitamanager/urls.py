from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from kitamanager.views_employee import (
    employee_list,
    employee_list_csv,
    employee_detail,
    employee_statistics,
    employee_bonuspayment,
    employeepayment_list,
    employeepayment_detail,
    employee_check_sage_payroll,
    employee_charts_count_group_by_area,
    employee_charts_hours_group_by_area,
)
from kitamanager.views_bank import bankaccount_list, bankaccount_charts_sum_balance_by_month
from kitamanager.views_child import (
    child_list,
    child_list_csv,
    child_list_future,
    child_detail,
    child_statistics,
    childpayment_list,
    childpayment_detail,
    child_charts_count_group_by_area,
    child_charts_count_by_month,
    child_charts_pay_income_vs_invoice,
)

from kitamanager.views_statistic import (
    statistic_charts_child_requirement_vs_employee_hours,
    statistic_charts_child_requirement_vs_employee_hours_percent,
)


app_name = "kitamanager"


urlpatterns = [
    # account
    path("accounts/login/", auth_views.LoginView.as_view(template_name="kitamanager/login.html"), name="login"),
    path("", TemplateView.as_view(template_name="kitamanager/index.html"), name="index"),
    # employee
    path("employeepayment/", employeepayment_list, name="employeepayment-list"),
    path("employeepayment/<str:plan>/", employeepayment_detail, name="employeepayment-detail"),
    path("employee/", employee_list, name="employee-list"),
    path("employee/csv/", employee_list_csv, name="employee-list-csv"),
    path("employee/statistics/", employee_statistics, name="employee-statistics"),
    path("employee/bonus/", employee_bonuspayment, name="employee-bonuspayment"),
    path("employee/check-sage-payroll", employee_check_sage_payroll, name="employee-check-sage-payroll"),
    path("employee/<int:pk>/", employee_detail, name="employee-detail"),
    path(
        "employee/charts/count-group-by-area/",
        employee_charts_count_group_by_area,
        name="employee-charts-count-group-by-area",
    ),
    path(
        "employee/charts/hours-group-by-area/",
        employee_charts_hours_group_by_area,
        name="employee-charts-hours-group-by-area",
    ),
    # child
    path("child/", child_list, name="child-list"),
    path("child/csv/", child_list_csv, name="child-list-csv"),
    path("child/future/", child_list_future, name="child-list-future"),
    path("child/statistics/", child_statistics, name="child-statistics"),
    path("child/<int:pk>/", child_detail, name="child-detail"),
    path(
        "child/charts/count-group-by-area/",
        child_charts_count_group_by_area,
        name="child-charts-count-group-by-area",
    ),
    path(
        "child/charts/count-by-month/",
        child_charts_count_by_month,
        name="child-charts-count-by-month",
    ),
    path(
        "child/charts/pay-income-vs-invoice/",
        child_charts_pay_income_vs_invoice,
        name="child-charts-pay-income-vs-invoice",
    ),
    path("childpayment/", childpayment_list, name="childpayment-list"),
    path("childpayment/<str:plan>/", childpayment_detail, name="childpayment-detail"),
    # statistics
    path(
        "statistic/charts/child-requirement-vs-employee-hours/",
        statistic_charts_child_requirement_vs_employee_hours,
        name="statistic-charts-child-requirement-vs-employee-hours",
    ),
    path(
        "statistic/charts/child-requirement-vs-employee-hours-percent/",
        statistic_charts_child_requirement_vs_employee_hours_percent,
        name="statistic-charts-child-requirement-vs-employee-hours-percent",
    ),
    # bankaccount
    path("bankaccount/", bankaccount_list, name="bankaccount-list"),
    path(
        "bankaccount/charts/sum-balance-by-month",
        bankaccount_charts_sum_balance_by_month,
        name="bankaccount-charts-sum-balance-by-month",
    ),
]
