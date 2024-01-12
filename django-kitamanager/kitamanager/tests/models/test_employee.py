import pytest
from decimal import Decimal
import math
from django.db.utils import IntegrityError
from dateutil.parser import parse

from kitamanager.models import Employee, EmployeePaymentPlan, EmployeePaymentTable, EmployeePaymentTableEntry
from kitamanager.tests.common import _employeecontract_create


@pytest.mark.django_db
def test_employee_create():
    """
    Create a single Employee and try the same Employee again
    """
    Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")

    # 2nd one with different first/last/birth should work
    Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")

    # 2nd one with same fist/last/birth is not allowed
    with pytest.raises(IntegrityError):
        Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")


@pytest.mark.django_db
def test_employee_begin_date():
    """
    Test the begin_date property without and with contract(s)
    """
    e = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    assert e.begin_date is None

    # with a contract
    _employeecontract_create(e, start="2019-01-01", end="2019-12-31")
    assert e.begin_date == parse("2019-01-01").date()

    # with an earlier contract
    _employeecontract_create(e, start="2010-01-01", end="2012-12-31")
    assert e.begin_date == parse("2010-01-01").date()


@pytest.mark.parametrize(
    "birth_date,check_date,expected",
    [
        ("2017-10-22", "2017-10-22", 0),
        ("2017-10-22", "2018-10-21", 0),
        ("2017-10-22", "2018-10-22", 1),
    ],
)
@pytest.mark.django_db
def test_employee_age(birth_date, check_date, expected):
    """
    Test the age() property
    """
    e = Employee.objects.create(first_name="1", last_name="11", birth_date=birth_date)
    e.refresh_from_db()
    assert e.age(parse(check_date).date()) == expected


@pytest.mark.django_db
def test_employee_salary():
    """
    Check Employee instance salary()
    """
    e1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    # there is no contract and no payplan
    assert e1.salary(parse("2020-01-01").date()) is None

    # a payment plan
    plan100 = EmployeePaymentPlan.objects.create(name="plan100")
    table100 = EmployeePaymentTable.objects.create(plan=plan100, hours=39, start="2020-01-01", end="2020-12-31")
    EmployeePaymentTableEntry.objects.create(table=table100, pay_group=1, pay_level=1, salary=100)
    EmployeePaymentTableEntry.objects.create(table=table100, pay_group=1, pay_level=2, salary=200)

    _employeecontract_create(
        e1,
        **{
            "start": "2010-01-01",
            "end": "2030-01-01",
            "hours_child": 10,
            "hours_management": 8,
            "hours_team": 6,
            "hours_misc": 4,
            "pay_group": 1,
            "pay_level": 2,
            "pay_plan": plan100,
        },
    )
    assert math.isclose(e1.salary(parse("2020-01-01").date()), Decimal(200 * 28.0 / 39.0))

    # outside of the PaymentTable dates
    assert e1.salary(parse("2022-01-01").date()) is None


@pytest.mark.django_db
def test_employee_pay_level_next():
    """
    Check Employee instance pay_level_next()
    """
    e = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    # there is no contract and no payplan
    assert e.pay_level_next(parse("2019-01-01").date()) is None

    _employeecontract_create(e, start="2019-01-01", end="2019-12-31", pay_level=1)
    # after a year, the next pay level should be reached
    assert e.pay_level_next(parse("2019-01-01").date()) == parse("2020-01-01").date()

    # but if the contract is already over, no next level
    assert e.pay_level_next(parse("2020-01-01").date()) is None

    # and also None if the latest pay level got already reached
    _employeecontract_create(e, start="2020-01-01", end="2021-01-01", pay_level=6)
    assert e.pay_level_next(parse("2020-01-01").date()) is None
