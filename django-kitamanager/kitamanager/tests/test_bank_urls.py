import os
import pytest
from decimal import Decimal
from dateutil.parser import parse
from psycopg2.extras import DateRange
from django.urls import reverse
from kitamanager.models import BankAccount, BankAccountEntry


@pytest.mark.django_db
def test_bankaccount_list(admin_client):
    response = admin_client.get(reverse("kitamanager:bankaccount-list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_bankaccount_import_do_fileupload(client):
    """
    Test the bankaccount import with real data
    """
    # there should be nothing
    assert BankAccount.objects.count() == 0
    # do the import
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "Kontostände 01.11.2023.xlsx")
    with open(f, "rb") as fp:
        response = client.post(reverse("admin:bankaccountentry-import"), {"file_xls": fp})
    assert response.status_code == 302

    # there should be 5 bank accounts now
    assert BankAccount.objects.count() == 5
    # check 1st account
    assert BankAccount.objects.get(name="GLS Bank").entries.count() == 1
    assert BankAccount.objects.get(name="GLS Bank").entries.first().date == DateRange(
        parse("2023-10-01").date(), parse("2023-11-01").date()
    )
    assert BankAccount.objects.get(name="GLS Bank").entries.first().balance == Decimal("20000.00")
    # check 2nd account
    assert BankAccount.objects.get(name="GLS Investitionen/Rücklagen").entries.count() == 1
    assert BankAccount.objects.get(name="GLS Investitionen/Rücklagen").entries.first().date == DateRange(
        parse("2023-10-01").date(), parse("2023-11-01").date()
    )
    assert BankAccount.objects.get(name="GLS Investitionen/Rücklagen").entries.first().balance == Decimal("10000.00")
    # check 3rd account
    assert BankAccount.objects.get(name="GLS Geschäftsguthaben").entries.count() == 1
    assert BankAccount.objects.get(name="GLS Geschäftsguthaben").entries.first().date == DateRange(
        parse("2023-10-01").date(), parse("2023-11-01").date()
    )
    assert BankAccount.objects.get(name="GLS Geschäftsguthaben").entries.first().balance == Decimal("1000.00")
    # check 4th account
    assert BankAccount.objects.get(name="Bank für Sozialwirtschaft").entries.count() == 1
    assert BankAccount.objects.get(name="Bank für Sozialwirtschaft").entries.first().date == DateRange(
        parse("2023-10-01").date(), parse("2023-11-01").date()
    )
    assert BankAccount.objects.get(name="Bank für Sozialwirtschaft").entries.first().balance == Decimal("50000.00")
    # check 5th account
    assert BankAccount.objects.get(name="Bank für Sozialwirt. Tagesgeld").entries.count() == 1
    assert BankAccount.objects.get(name="Bank für Sozialwirt. Tagesgeld").entries.first().date == DateRange(
        parse("2023-10-01").date(), parse("2023-11-01").date()
    )
    assert BankAccount.objects.get(name="Bank für Sozialwirt. Tagesgeld").entries.first().balance == Decimal("20000.00")


@pytest.mark.django_db
def test_bankaccount_charts_sum_balance_by_month_no_data(admin_client):
    # without any data
    response = admin_client.get(
        reverse("kitamanager:bankaccount-charts-sum-balance-by-month"), {"historydate": "2019-01-21"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["labels"] == [
        "2017-10",
        "2017-11",
        "2017-12",
        "2018-01",
        "2018-02",
        "2018-03",
        "2018-04",
        "2018-05",
        "2018-06",
        "2018-07",
        "2018-08",
        "2018-09",
        "2018-10",
        "2018-11",
        "2018-12",
        "2019-01",
        "2019-02",
        "2019-03",
        "2019-04",
    ]
    assert len(response.json()["data"]["datasets"]) == 1
    assert len(response.json()["data"]["labels"]) == len(response.json()["data"]["datasets"][0]["data"])
    assert response.json()["data"]["datasets"][0]["data"] == ["0"] * 19


@pytest.mark.django_db
def test_bankaccount_charts_sum_balance_by_month_with_data(admin_client):
    # with some data
    ba1 = BankAccount.objects.create(name="ba1")
    BankAccountEntry.objects.create(bankaccount=ba1, date=["2017-08-01", "2017-10-22"], balance="200")
    BankAccountEntry.objects.create(bankaccount=ba1, date=["2018-01-01", "2018-04-01"], balance="100")
    BankAccountEntry.objects.create(bankaccount=ba1, date=["2019-03-01", "2020-04-01"], balance="300")

    # with a second BankAccount
    ba2 = BankAccount.objects.create(name="ba2")
    BankAccountEntry.objects.create(bankaccount=ba2, date=["2018-03-01", "2018-05-01"], balance="30")
    BankAccountEntry.objects.create(bankaccount=ba2, date=["2020-01-01", "2020-02-01"], balance="30")

    response = admin_client.get(
        reverse("kitamanager:bankaccount-charts-sum-balance-by-month"), {"historydate": "2019-01-21"}
    )
    assert len(response.json()["data"]["datasets"]) == 1
    assert len(response.json()["data"]["labels"]) == len(response.json()["data"]["datasets"][0]["data"])
    assert response.json()["data"]["datasets"][0]["data"] == [
        "200.00",
        "0",
        "0",
        "100.00",
        "100.00",
        "130.00",
        "30.00",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "300.00",
        "300.00",
    ]
