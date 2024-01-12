import pytest
from django.urls import reverse
from kitamanager.models import Child, ChildPaymentPlan, ChildPaymentTable, ChildPaymentTableEntry
from kitamanager.tests.common import _childcontract_create, _childpaymentplan_create


@pytest.mark.django_db
def test_child_list(admin_client):
    response = admin_client.get(reverse("kitamanager:child-list"))
    assert response.context["object_list"].count() == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_list_with_child_no_contract(admin_client):
    Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    response = admin_client.get(reverse("kitamanager:child-list"))
    assert response.context["object_list"].count() == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_list_with_child_with_contract(admin_client):
    c1 = Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _childpaymentplan_create()
    _childcontract_create(c1, start="2018-01-01", end="2022-01-01")
    response = admin_client.get(reverse("kitamanager:child-list"))
    assert response.context["object_list"].count() == 0
    response = admin_client.get(reverse("kitamanager:child-list") + "?historydate=2020-06-01")
    assert response.context["object_list"].count() == 1
    # now query with correct historydate
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_detail(admin_client):
    e = Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    # response without a contract
    response = admin_client.get(reverse("kitamanager:child-detail", args=[e.pk]))
    assert response.status_code == 200
    # response with a contract
    _childcontract_create(e, start="2019-01-01", end="2019-12-31")
    response = admin_client.get(reverse("kitamanager:child-detail", args=[e.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_statistics(admin_client):
    # response without data
    response = admin_client.get(reverse("kitamanager:child-statistics"))
    # with some data
    e = Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _childcontract_create(e, start="2019-01-01", end="2019-12-31")
    response = admin_client.get(reverse("kitamanager:child-statistics") + "?historydate=2020-06-01")
    assert response.status_code == 200


@pytest.mark.django_db
def test_childpayment_list(admin_client):
    # response without a payment plan
    response = admin_client.get(reverse("kitamanager:childpayment-list"))
    assert response.status_code == 200

    ChildPaymentPlan.objects.create(name="plan1")
    # response with a payment plan
    response = admin_client.get(reverse("kitamanager:childpayment-list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_childpayment_detail(admin_client):
    # response with a plan
    p = ChildPaymentPlan.objects.create(name="plan1")
    t = ChildPaymentTable.objects.create(plan=p, start="2020-01-01", end="2020-12-31")
    ChildPaymentTableEntry.objects.create(table=t, age=[0, 1], name="ganztag", pay=100, requirement=0.1)

    response = admin_client.get(reverse("kitamanager:childpayment-detail", args=[p.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_charts_count_by_month(admin_client):
    """
    Test the child_charts_count_by_month() view which returns json
    """
    # without any data
    response = admin_client.get(reverse("kitamanager:child-charts-count-by-month") + "?historydate=2020-06-01")
    assert response.status_code == 200
    assert response.json()["title"] == "Children count by month"
    assert response.json()["data"]["labels"] == [
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember",
    ]
    assert response.json()["data"]["datasets"] == [
        {"label": 2017, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#ffa600"},
        {"label": 2018, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#ff6361"},
        {"label": 2019, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#bc5090"},
        {"label": 2020, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#58508d"},
        {"label": 2021, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#003f5c"},
        {"label": 2022, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#444e86"},
    ]

    # with some data
    e = Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _childcontract_create(e, start="2019-01-01", end="2019-12-31")
    response = admin_client.get(reverse("kitamanager:child-charts-count-by-month") + "?historydate=2020-06-01")
    assert response.status_code == 200
    assert response.json()["data"]["datasets"] == [
        {"label": 2017, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#ffa600"},
        {"label": 2018, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#ff6361"},
        {"label": 2019, "data": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "backgroundColor": "#bc5090"},
        {"label": 2020, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#58508d"},
        {"label": 2021, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#003f5c"},
        {"label": 2022, "data": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "backgroundColor": "#444e86"},
    ]
