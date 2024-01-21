import pytest
import os
from django.urls import reverse
from kitamanager.models import RevenueName, RevenueEntry

"""
Testing access to different URLs
"""


def test_admin_bankaccountentry_changelist(admin_client):
    response = admin_client.get(reverse("admin:kitamanager_bankaccountentry_changelist"))
    assert response.status_code == 200


def test_admin_bankaccountentry_changelist_import(admin_client):
    response = admin_client.get(reverse("admin:bankaccountentry-import"))
    assert response.status_code == 200


def test_admin_revenueentry_changelist(admin_client):
    response = admin_client.get(reverse("admin:kitamanager_revenueentry_changelist"))
    assert response.status_code == 200


def test_admin_revenueentry_berlin_import(admin_client):
    response = admin_client.get(reverse("admin:revenueentry-berlin-import"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_revenueentry_berlin_import_with_data(admin_client):
    """
    Do a real import via the admin interface
    """
    assert RevenueName.objects.count() == 0
    assert RevenueEntry.objects.count() == 0
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "berlin", "e_Abrechnung_09-22_0770.xlsx")
    with open(f, "rb") as fp:
        response = admin_client.post(reverse("admin:revenueentry-berlin-import"), data={"file_xls": fp})
    assert response.status_code == 302
    assert RevenueName.objects.count() == 1
    assert RevenueEntry.objects.count() == 1
