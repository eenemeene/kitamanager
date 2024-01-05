import pytest
from django.urls import reverse
from kitamanager.tests.common import _employeecontract_create
from kitamanager.models import Employee, EmployeePaymentPlan, EmployeeQualification, Area
from dateutil.parser import parse
from psycopg2.extras import DateRange

"""
Testing access to different URLs
"""


@pytest.mark.django_db
def test_employee_list(client):
    # without data
    response = client.get(reverse("kitamanager:employee-list"))
    assert response.status_code == 200
    # with data
    e = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(e, date=["2019-01-01", "2019-12-31"])
    response = client.get(reverse("kitamanager:employee-list") + "?historydate=2019-01-01")
    assert response.context["object_list"].count() == 1
    assert response.status_code == 200


@pytest.mark.django_db
def test_employee_detail(client):
    e = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    # response without a contract
    response = client.get(reverse("kitamanager:employee-detail", args=[e.pk]))
    assert response.status_code == 200
    # response with a contract
    _employeecontract_create(e, date=["2019-01-01", "2019-12-31"])
    response = client.get(reverse("kitamanager:employee-detail", args=[e.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_employeepayment_list(client):
    response = client.get(reverse("kitamanager:employeepayment-list"))
    assert response.status_code == 200

    EmployeePaymentPlan.objects.create(name="plan1")
    response = client.get(reverse("kitamanager:employeepayment-list"))
    assert response.context["object_list"].count() == 1
    assert response.status_code == 200
    assert "plan1" in response.content.decode()


@pytest.mark.django_db
def test_employeepayment_detail(client):
    # should be 404 for an unknown EmployeePaymentPlan
    response = client.get(reverse("kitamanager:employeepayment-detail", args=["unknown"]))
    assert response.status_code == 404

    EmployeePaymentPlan.objects.create(name="plan1")
    response = client.get(reverse("kitamanager:employeepayment-detail", args=["plan1"]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_employee_charts_hours_group_by_area(client):
    """
    Test the json response for employee charts hours group by area
    """
    response = client.get(reverse("kitamanager:employee-charts-hours-group-by-area"))
    assert response.status_code == 200

    # with some data
    e1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(e1, date=["2019-01-01", "2019-12-31"])

    area = Area.objects.create(name="area2", educational=True)
    e2 = Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")
    _employeecontract_create(e2, date=["2019-06-01", "2022-12-31"], area=area)

    # historydate only for e1
    response = client.get(reverse("kitamanager:employee-charts-hours-group-by-area"), {"historydate": "2019-01-01"})
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1"]

    # historydate for e1 and e2
    response = client.get(reverse("kitamanager:employee-charts-hours-group-by-area"), {"historydate": "2019-06-01"})
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1", "area2"]


@pytest.mark.django_db
def test_employee_charts_count_group_by_area(client):
    """
    Test the json response for employee charts count group by area
    """
    response = client.get(reverse("kitamanager:employee-charts-count-group-by-area"))
    assert response.status_code == 200

    # with some data
    e1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(e1, date=["2019-01-01", "2019-12-31"])

    area = Area.objects.create(name="area2", educational=True)
    e2 = Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")
    _employeecontract_create(e2, date=["2019-06-01", "2022-12-31"], area=area)

    # historydate only for e1
    response = client.get(reverse("kitamanager:employee-charts-count-group-by-area"), {"historydate": "2019-01-01"})
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1"]

    # historydate for e1 and e2
    response = client.get(reverse("kitamanager:employee-charts-count-group-by-area"), {"historydate": "2019-06-01"})
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == ["area1", "area2"]
