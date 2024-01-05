import pytest
import datetime
from decimal import Decimal
import math
from django.db.utils import IntegrityError
from dateutil.parser import parse
from psycopg2.extras import DateRange
from kitamanager.models import Child, ChildContract
from kitamanager.tests.common import _childcontract_create


@pytest.mark.parametrize(
    "setup,check_date,expected",
    [
        (
            # setup
            {
                "c1": [["2021-01-01", "2021-12-31"], ["2022-01-01", "2022-12-31"]],
                "c2": [["2010-01-01", "2014-12-31"], ["2015-01-01", "2015-12-31"]],
            },
            # check_date
            "2020-01-01",
            # expected
            {},
        ),
        (
            {
                "c1": [["2021-01-01", "2021-12-31"], ["2022-01-01", "2022-12-31"]],
                "c2": [["2010-01-01", "2014-12-31"], ["2015-01-01", "2015-12-31"]],
            },
            "2015-01-01",
            {
                "c2": DateRange(parse("2015-01-01").date(), parse("2015-12-31").date()),
            },
        ),
        (
            {
                "c1": [["2021-01-01", "2021-12-31"], ["2022-01-01", "2022-12-31"]],
                "c2": [["2010-01-01", "2014-12-31"], ["2015-01-01", "2015-12-31"]],
            },
            "2022-01-01",
            {
                "c1": DateRange(parse("2022-01-01").date(), parse("2022-12-31").date()),
            },
        ),
    ],
)
@pytest.mark.django_db
def test_childcontract_manager_by_date(setup, check_date, expected):
    """
    Check ChildContractManager by_date() with multiple contracts
    """
    # setup
    for child, contracts in setup.items():
        ch = Child.objects.create(first_name=child, last_name=child, birth_date="2017-10-22")
        for contract_dates in contracts:
            _childcontract_create(ch, date=contract_dates)

    # check
    for expected_child, expected_contract in expected.items():
        res = ChildContract.objects.by_date(parse(check_date))
        assert res.count() == len(expected.keys())

        assert res.get(person__first_name=expected_child, person__last_name=expected_child).date == expected_contract


@pytest.mark.django_db
def test_childcontract_payment_outside_contract():
    """
    Test the payment() method but with a date outside of the contract date
    """
    c = Child.objects.create(first_name="1", last_name="11", birth_date="2020-06-29")
    c.refresh_from_db()
    cc = _childcontract_create(c, date=["2023-01-01", "2024-01-01"])
    cc.refresh_from_db()
    # test outside of contract

    with pytest.raises(ValueError):
        assert cc.payment(parse("2022-06-29").date())


@pytest.mark.django_db
def test_childcontract_payment():
    """
    Test the payment() method
    """
    c = Child.objects.create(first_name="1", last_name="11", birth_date="2020-06-29")
    c.refresh_from_db()
    cc1 = _childcontract_create(c, date=["2022-01-01", "2023-01-01"])
    cc1.refresh_from_db()
    # test inside of contract but no plan table entry for that date
    assert cc1.payment(parse("2022-06-29").date()) is None

    # create a contract where a ChildPaymentTable exists for (but no ChildPaymentTableEntry, see _childcontract_create())
    cc2 = _childcontract_create(c, date=["2021-01-01", "2021-05-01"], pay_tags=["does not exist"])
    cc2.refresh_from_db()
    assert cc2.payment(parse("2021-04-01").date()) is None

    # create a contract where a ChildPaymentTable exists for and also a pay_tag, but the age doesn't match
    cc3 = _childcontract_create(c, date=["2021-07-01", "2021-08-01"], pay_tags=["ganztag"])
    cc3.refresh_from_db()
    assert cc3.person.age(parse("2021-07-05").date()) == 1
    assert cc3.payment(parse("2021-07-05").date()) == Decimal("200")

    # test the "base" tag
    cc4 = _childcontract_create(c, date=["2024-01-01", "2024-02-01"], pay_tags=["ganztag"])
    cc4.refresh_from_db()
    assert cc4.person.age(parse("2024-01-05").date()) == 3
    assert cc4.payment(parse("2024-01-05").date()) == Decimal("322")


@pytest.mark.django_db
def test_childcontract_requirement_outside_contract():
    """
    Test the requirement() method but with a date outside of the contract date
    """
    c = Child.objects.create(first_name="1", last_name="11", birth_date="2020-06-29")
    c.refresh_from_db()
    cc = _childcontract_create(c, date=["2023-01-01", "2024-01-01"])
    cc.refresh_from_db()
    # test outside of contract

    with pytest.raises(ValueError):
        assert cc.requirement(parse("2022-06-29").date())


@pytest.mark.django_db
def test_childcontract_requirement():
    """
    Test the requirement() method
    """
    c = Child.objects.create(first_name="1", last_name="11", birth_date="2020-06-29")
    c.refresh_from_db()
    cc1 = _childcontract_create(c, date=["2022-01-01", "2023-01-01"])
    cc1.refresh_from_db()
    # test inside of contract but no plan table entry for that date
    assert cc1.requirement(parse("2022-06-29").date()) is None

    # create a contract where a ChildPaymentTable exists for (but no ChildPaymentTableEntry, see _childcontract_create())
    cc2 = _childcontract_create(c, date=["2021-01-01", "2021-05-01"], pay_tags=["does not exist"])
    cc2.refresh_from_db()
    assert cc2.requirement(parse("2021-04-01").date()) is None

    # create a contract where a ChildPaymentTable exists for and also a pay_tag, but the age doesn't match
    cc3 = _childcontract_create(c, date=["2021-07-01", "2021-08-01"], pay_tags=["ganztag"])
    cc3.refresh_from_db()
    assert cc3.person.age(parse("2021-07-05").date()) == 1
    assert cc3.requirement(parse("2021-07-05").date()) == Decimal("0.1")

    # test the "base" tag
    cc4 = _childcontract_create(c, date=["2024-01-01", "2024-02-01"], pay_tags=["ganztag"])
    cc4.refresh_from_db()
    assert cc4.person.age(parse("2024-01-05").date()) == 3
    assert cc4.requirement(parse("2024-01-05").date()) == Decimal("0.53")


@pytest.mark.django_db
def test_childcontract_sum_payment():
    """
    Test the sum_payment() ChildContractManager method
    """
    c1 = Child.objects.create(first_name="1", last_name="11", birth_date="2020-06-29")
    c1.refresh_from_db()

    cc1 = _childcontract_create(c1, date=["2021-07-01", "2021-08-01"], pay_tags=["ganztag"])
    cc1.refresh_from_db()

    c2 = Child.objects.create(first_name="2", last_name="22", birth_date="2020-06-29")
    c2.refresh_from_db()

    cc2 = _childcontract_create(c2, date=["2021-07-01", "2025-01-01"], pay_tags=["ganztag"])
    cc2.refresh_from_db()

    # without any child contract, it should be 0
    assert ChildContract.objects.sum_payments(parse("1981-03-29").date()) == 0

    # with both child contracts
    assert ChildContract.objects.sum_payments(parse("2021-07-01").date()) == Decimal("400")

    # with single child contract
    assert ChildContract.objects.sum_payments(parse("2024-01-01").date()) == Decimal("322")
