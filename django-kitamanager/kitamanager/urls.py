from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from kitamanager.views_employee import (
    employee_list,
    EmployeeDetailView,
    employeepayment_list,
    employeepayment_detail,
    employee_charts_count_group_by_area,
    employee_charts_hours_group_by_area,
)
from kitamanager.views_bank import bankaccount_list, bankaccount_charts_sum_balance_by_month
from kitamanager.views_child import (
    child_list,
    child_detail,
    childpayment_list,
    childpayment_detail,
    child_charts_count_group_by_area,
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
    path("employee/<int:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),
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
    path("child/<int:pk>/", child_detail, name="child-detail"),
    path(
        "child/charts/count-group-by-area/",
        child_charts_count_group_by_area,
        name="child-charts-count-group-by-area",
    ),
    path("childpayment/", childpayment_list, name="childpayment-list"),
    path("childpayment/<str:plan>/", childpayment_detail, name="childpayment-detail"),
    # bankaccount
    path("bankaccount/", bankaccount_list, name="bankaccount-list"),
    path(
        "bankaccount/charts/sum-balance-by-month",
        bankaccount_charts_sum_balance_by_month,
        name="bankaccount-charts-sum-balance-by-month",
    ),
]
