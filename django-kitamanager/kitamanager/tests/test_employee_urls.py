import pytest
import datetime
from django.urls import reverse
from kitamanager.tests.common import _employeecontract_create
from kitamanager.models import Employee, EmployeePaymentPlan, Area

"""
Testing access to different URLs
"""


@pytest.mark.django_db
def test_employee_list(admin_client):
    # without data
    response = admin_client.get(reverse("kitamanager:employee-list"))
    assert response.status_code == 200
    # with data
    e = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(e, start="2019-01-01", end="2019-12-31")
    response = admin_client.get(reverse("kitamanager:employee-list") + "?historydate=2019-01-01")
    assert response.context["object_list"].count() == 1
    assert response.status_code == 200


@pytest.mark.django_db
def test_employee_list_csv(admin_client):
    historydate = datetime.date.today()
    response = admin_client.get(reverse("kitamanager:employee-list-csv"))
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv"
    assert response.headers["Content-Disposition"] == f'attachment; filename="employee-list-{historydate}.csv"'
    assert (
        response.content.decode() == "ID,First Name,Last Name,Begin date,pay plan,pay group,pay level,pay "
        "level next,area,qualification,hours child per week,hours management per week,"
        "hours team per week,hours misc per week,monthly salary (Euro)\r\n"
    )


@pytest.mark.django_db
def test_employee_detail(admin_client):
    e = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    # response without a contract
    response = admin_client.get(reverse("kitamanager:employee-detail", args=[e.pk]))
    assert response.status_code == 200
    # response with a contract
    _employeecontract_create(e, start="2019-01-01", end="2019-12-31")
    response = admin_client.get(reverse("kitamanager:employee-detail", args=[e.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_employeepayment_list(admin_client):
    response = admin_client.get(reverse("kitamanager:employeepayment-list"))
    assert response.status_code == 200

    EmployeePaymentPlan.objects.create(name="plan1")
    response = admin_client.get(reverse("kitamanager:employeepayment-list"))
    assert response.context["object_list"].count() == 1
    assert response.status_code == 200
    assert "plan1" in response.content.decode()


@pytest.mark.django_db
def test_employeepayment_detail(admin_client):
    # should be 404 for an unknown EmployeePaymentPlan
    response = admin_client.get(reverse("kitamanager:employeepayment-detail", args=["unknown"]))
    assert response.status_code == 404

    EmployeePaymentPlan.objects.create(name="plan1")
    response = admin_client.get(reverse("kitamanager:employeepayment-detail", args=["plan1"]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_employee_check_sage_payroll(admin_client):
    # should be 404 for an unknown EmployeePaymentPlan
    response = admin_client.get(reverse("kitamanager:employee-check-sage-payroll"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_employee_charts_hours_group_by_area(admin_client):
    """
    Test the json response for employee charts hours group by area
    """
    response = admin_client.get(reverse("kitamanager:employee-charts-hours-group-by-area"))
    assert response.status_code == 200

    # with some data
    e1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(e1, start="2019-01-01", end="2019-12-31")

    area = Area.objects.create(name="area2", educational=True)
    e2 = Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")
    _employeecontract_create(e2, start="2019-06-01", end="2022-12-31", area=area)

    # historydate only for e1
    response = admin_client.get(
        reverse("kitamanager:employee-charts-hours-group-by-area"), {"historydate": "2019-01-01"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1"]

    # historydate for e1 and e2
    response = admin_client.get(
        reverse("kitamanager:employee-charts-hours-group-by-area"), {"historydate": "2019-06-01"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1", "area2"]


@pytest.mark.django_db
def test_employee_charts_count_group_by_area(admin_client):
    """
    Test the json response for employee charts count group by area
    """
    response = admin_client.get(reverse("kitamanager:employee-charts-count-group-by-area"))
    assert response.status_code == 200

    # with some data
    e1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(e1, start="2019-01-01", end="2019-12-31")

    area = Area.objects.create(name="area2", educational=True)
    e2 = Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")
    _employeecontract_create(e2, start="2019-06-01", end="2022-12-31", area=area)

    # historydate only for e1
    response = admin_client.get(
        reverse("kitamanager:employee-charts-count-group-by-area"), {"historydate": "2019-01-01"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1"]

    # historydate for e1 and e2
    response = admin_client.get(
        reverse("kitamanager:employee-charts-count-group-by-area"), {"historydate": "2019-06-01"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1", "area2"]
