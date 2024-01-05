import pytest
import datetime
from decimal import Decimal
import math
from django.db.utils import IntegrityError
from dateutil.parser import parse
from kitamanager.models import Child, ChildContract
from kitamanager.tests.common import _childcontract_create


@pytest.mark.django_db
def test_child_create():
    """
    Create a single Child and try the same Child again
    """
    Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")

    # 2nd one with different first/last/birth should work
    Child.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")

    # 2nd one with same fist/last/birth is not allowed
    with pytest.raises(IntegrityError):
        Child.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")


@pytest.mark.parametrize(
    "contracts,expected",
    [
        ([], None),
        (
            [
                ["2019-01-01", "2019-12-31"],
            ],
            parse("2019-01-01").date(),
        ),
        ([["2019-01-01", "2019-12-31"], ["2010-01-01", "2012-12-31"]], parse("2010-01-01").date()),
        ([["2012-01-01", "2013-01-01"], ["2013-01-01", "2015-01-01"]], parse("2012-01-01").date()),
    ],
)
@pytest.mark.django_db
def test_child_begin_date(contracts, expected):
    """
    Test the begin_date property without and with contract(s)
    """
    c = Child.objects.create(first_name="1", last_name="11", birth_date="2000-01-01")
    for con in contracts:
        _childcontract_create(c, date=con)
    assert c.begin_date == expected


@pytest.mark.parametrize(
    "birth_date,check_date,expected",
    [
        ("2017-10-22", "2017-10-22", 0),
        ("2017-10-22", "2018-10-21", 0),
        ("2017-10-22", "2018-10-22", 1),
    ],
)
@pytest.mark.django_db
def test_child_age(birth_date, check_date, expected):
    """
    Test the age() property
    """
    e = Child.objects.create(first_name="1", last_name="11", birth_date=birth_date)
    e.refresh_from_db()
    assert e.age(parse(check_date).date()) == expected
