import pytest
from django.db.utils import IntegrityError
from dateutil.parser import parse
from decimal import Decimal

from kitamanager.models import BankAccount, BankAccountEntry


@pytest.mark.django_db
def test_bankaccount_create():
    """
    Create a single BankAccount
    """
    BankAccount.objects.create(name="ba1")

    # 2nd one with different name should work
    BankAccount.objects.create(name="ba2")

    # 2nd one with same name is not allowed
    with pytest.raises(IntegrityError):
        BankAccount.objects.create(name="ba2")


@pytest.mark.django_db
def test_bankaccountentry_create():
    """
    Create BankAccountEntry's
    """
    ba1 = BankAccount.objects.create(name="ba1")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-01-01", end="2020-01-31", balance="100")

    # 2nd entry with non-overlapping date should work
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-02-01", end="2020-02-28", balance="100")

    # entry with overlapping date within other bank account should work
    ba2 = BankAccount.objects.create(name="ba2")
    BankAccountEntry.objects.create(bankaccount=ba2, start="2020-01-01", end="2020-01-31", balance="100")

    # 2nd entry with overlapping date shouldn't work
    with pytest.raises(IntegrityError):
        BankAccountEntry.objects.create(bankaccount=ba1, start="2020-02-01", end="2020-02-28", balance="100")


@pytest.mark.django_db
def test_bankaccountentry_by_date():
    """
    Test BankAccountEntry by_date()
    """
    ba1 = BankAccount.objects.create(name="ba1")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-01-01", end="2020-01-31", balance="100")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-02-01", end="2020-02-28", balance="100")

    # outside of date range
    assert BankAccountEntry.objects.by_date(parse("2010-01-01")).count() == 0

    # inside of date range
    assert BankAccountEntry.objects.by_date(parse("2020-01-01")).count() == 1

    # with a second BankAccount
    ba2 = BankAccount.objects.create(name="ba2")
    BankAccountEntry.objects.create(bankaccount=ba2, start="2020-01-01", end="2020-01-31", balance="100")

    # inside of date range
    assert BankAccountEntry.objects.by_date(parse("2020-01-01")).count() == 2


@pytest.mark.django_db
def test_bankaccountentry_sum_balance():
    """
    Test BankAccountEntry sum_balance()
    """
    ba1 = BankAccount.objects.create(name="ba1")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-01-01", end="2020-02-01", balance="100")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-02-01", end="2020-03-01", balance="200")

    # outside of date range
    assert BankAccountEntry.objects.sum_balance(parse("2010-01-01"))["balance_sum"] == 0

    # inside of date range
    assert BankAccountEntry.objects.sum_balance(parse("2020-01-01"))["balance_sum"] == 100
    assert BankAccountEntry.objects.sum_balance(parse("2020-02-01"))["balance_sum"] == 200

    # with a second BankAccount
    ba2 = BankAccount.objects.create(name="ba2")
    BankAccountEntry.objects.create(bankaccount=ba2, start="2020-01-01", end="2020-01-31", balance="30")

    # inside of date range
    assert BankAccountEntry.objects.sum_balance(parse("2020-01-01"))["balance_sum"] == 130
    assert BankAccountEntry.objects.sum_balance(parse("2020-02-28"))["balance_sum"] == 200


@pytest.mark.django_db
def test_bankaccountentry_sum_balance_by_month():
    ba1 = BankAccount.objects.create(name="ba1")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-01-01", end="2020-02-01", balance="100")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-02-01", end="2020-03-01", balance="200")
    BankAccountEntry.objects.create(bankaccount=ba1, start="2020-03-01", end="2020-04-01", balance="300")

    # with a second BankAccount
    ba2 = BankAccount.objects.create(name="ba2")
    BankAccountEntry.objects.create(bankaccount=ba2, start="2020-01-01", end="2020-02-01", balance="30")

    # outside of any BankAccountEntry
    assert BankAccountEntry.objects.sum_balance_by_month(parse("2010-01-01").date(), parse("2010-02-01").date()) == {
        parse("2010-01-01").date(): Decimal("0"),
        parse("2010-02-01").date(): Decimal("0"),
    }

    # outside of any BankAccountEntry with days within a month
    assert BankAccountEntry.objects.sum_balance_by_month(parse("2010-01-15").date(), parse("2010-02-13").date()) == {
        parse("2010-01-15").date(): Decimal("0"),
    }

    # within multiple BankAccountEntry's
    assert BankAccountEntry.objects.sum_balance_by_month(parse("2020-01-01").date(), parse("2020-01-01").date()) == {
        parse("2020-01-01").date(): Decimal("130"),
    }

    assert BankAccountEntry.objects.sum_balance_by_month(parse("2020-01-01").date(), parse("2020-02-01").date()) == {
        parse("2020-01-01").date(): Decimal("130"),
        parse("2020-02-01").date(): Decimal("200"),
    }
