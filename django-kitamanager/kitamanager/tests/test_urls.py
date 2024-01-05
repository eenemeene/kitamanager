import pytest
from django.urls import reverse
from kitamanager.tests.common import _employeecontract_create
from kitamanager.models import Employee, EmployeePaymentPlan, Area

"""
Testing access to different URLs
"""


def test_index(client):
    response = client.get(reverse("kitamanager:index"))
    assert response.status_code == 200
    assert ":)" in response.content.decode()
