import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_statistic_charts_child_requirement_vs_employee_hours(admin_client):
    """
    Test the statistic_charts_child_requirement_vs_employee_hours() view which returns json
    """
    # without any data
    response = admin_client.get(
        reverse("kitamanager:statistic-charts-child-requirement-vs-employee-hours") + "?historydate=2020-06-01"
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Children requirements vs. Employee working hours"
    assert response.json()["data"]["labels"] == [
        "2019-06",
        "2019-07",
        "2019-08",
        "2019-09",
        "2019-10",
        "2019-11",
        "2019-12",
        "2020-01",
        "2020-02",
        "2020-03",
        "2020-04",
        "2020-05",
        "2020-06",
        "2020-07",
        "2020-08",
        "2020-09",
        "2020-10",
        "2020-11",
    ]
