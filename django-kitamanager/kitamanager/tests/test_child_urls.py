import pytest
from django.urls import reverse
from kitamanager.models import Child
from kitamanager.tests.common import _childcontract_create, _childpaymentplan_create


@pytest.mark.django_db
def test_child_list(client):
    response = client.get(reverse("kitamanager:child-list"))
    assert response.context["object_list"].count() == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_list_with_child_no_contract(client):
    c1 = Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    response = client.get(reverse("kitamanager:child-list"))
    assert response.context["object_list"].count() == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_list_with_child_with_contract(client):
    c1 = Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _childpaymentplan_create()
    _childcontract_create(c1, date=["2018-01-01", "2022-01-01"])
    response = client.get(reverse("kitamanager:child-list"))
    assert response.context["object_list"].count() == 0
    response = client.get(reverse("kitamanager:child-list") + f"?historydate=2020-06-01")
    assert response.context["object_list"].count() == 1
    # now query with correct historydate
    assert response.status_code == 200


@pytest.mark.django_db
def test_child_detail(client):
    e = Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    # response without a contract
    response = client.get(reverse("kitamanager:child-detail", args=[e.pk]))
    assert response.status_code == 200
    # response with a contract
    _childcontract_create(e, date=["2019-01-01", "2019-12-31"])
    response = client.get(reverse("kitamanager:child-detail", args=[e.pk]))
    assert response.status_code == 200
