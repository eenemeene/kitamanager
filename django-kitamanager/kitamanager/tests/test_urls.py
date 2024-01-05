from django.urls import reverse

"""
Testing access to different URLs
"""


def test_index(client):
    response = client.get(reverse("kitamanager:index"))
    assert response.status_code == 200
    assert ":)" in response.content.decode()
