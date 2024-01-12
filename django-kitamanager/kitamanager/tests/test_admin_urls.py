from django.urls import reverse

"""
Testing access to different URLs
"""


def test_admin_bankaccountentry_changelist(admin_client):
    response = admin_client.get(reverse("admin:kitamanager_bankaccountentry_changelist"))
    assert response.status_code == 200


def test_admin_bankaccountentry_changelist_import(admin_client):
    response = admin_client.get(reverse("admin:bankaccountentry-import"))
    assert response.status_code == 200
