import pytest
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from decimal import Decimal
from dateutil.parser import parse
from psycopg2.extras import DateRange
from kitamanager.models import Area, Employee, EmployeeContract, EmployeeQualification
from kitamanager.tests.common import _employeecontract_create, _employeepaymentplan_create


@pytest.mark.django_db
def test_employeecontract_create():
    """
    Create a single EmployeeContract and try the same contract date again
    """
    e1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    e2 = Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")

    # multiple employeecontract should work
    _employeecontract_create(e1, date=["2020-01-01", "2020-12-31"])
    _employeecontract_create(e1, date=["2019-01-01", "2019-12-31"])
    _employeecontract_create(e1, date=["2021-01-01", "2021-12-31"])

    # same employeecontract for other employee should work
    _employeecontract_create(e2, date=["2020-01-01", "2020-12-31"])

    # same employeecontract for same employee shouldn't work
    with pytest.raises(IntegrityError):
        _employeecontract_create(e1, date=["2020-01-01", "2020-12-31"])


@pytest.mark.django_db
def test_employeecontract_hours_total():
    """
    Test the EmployeeContract property hours_total()
    """
    e1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")

    ec1 = _employeecontract_create(
        e1, date=["2020-01-01", "2020-12-31"], hours_child=1, hours_management=2, hours_team=2, hours_misc=2
    )
    assert ec1.hours_total == 7


@pytest.mark.django_db
def test_employeecontract_bydate_all_no_contract():
    """
    Check EmployeeContractManager by_date() without any contract
    """
    # without any employee and contract
    assert EmployeeContract.objects.by_date(parse("2020-01-01")).count() == 0

    # with a employee but still without a contract
    Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    assert EmployeeContract.objects.by_date(parse("2020-01-01")).count() == 0


@pytest.mark.parametrize(
    "setup,check_date,expected",
    [
        (
            # setup
            {
                "e1": [["2021-01-01", "2021-12-31"], ["2022-01-01", "2022-12-31"]],
                "e2": [["2010-01-01", "2014-12-31"], ["2015-01-01", "2015-12-31"]],
            },
            # check_date
            "2020-01-01",
            # expected
            {},
        ),
        (
            {
                "e1": [["2021-01-01", "2021-12-31"], ["2022-01-01", "2022-12-31"]],
                "e2": [["2010-01-01", "2014-12-31"], ["2015-01-01", "2015-12-31"]],
            },
            "2015-01-01",
            {
                "e2": DateRange(parse("2015-01-01").date(), parse("2015-12-31").date()),
            },
        ),
        (
            {
                "e1": [["2021-01-01", "2021-12-31"], ["2022-01-01", "2022-12-31"]],
                "e2": [["2010-01-01", "2014-12-31"], ["2015-01-01", "2015-12-31"]],
            },
            "2022-01-01",
            {
                "e1": DateRange(parse("2022-01-01").date(), parse("2022-12-31").date()),
            },
        ),
    ],
)
@pytest.mark.django_db
def test_employeecontract_manager_by_date(setup, check_date, expected):
    """
    Check EmployeeContractManager by_date() with multiple contracts
    """
    # setup
    for employee, contracts in setup.items():
        emp = Employee.objects.create(first_name=employee, last_name=employee, birth_date="2017-10-22")
        for contract_dates in contracts:
            _employeecontract_create(emp, date=contract_dates)

    # check
    for expected_employee, expected_contract in expected.items():
        res = EmployeeContract.objects.by_date(parse(check_date))
        assert res.count() == len(expected.keys())

        assert (
            res.get(person__first_name=expected_employee, person__last_name=expected_employee).date == expected_contract
        )


@pytest.mark.django_db
def test_employeecontract_sum_hours():
    """
    Check EmployeeContract sum_hours()
    """
    # without any data
    res = EmployeeContract.objects.sum_hours(parse("2020-01-01"))
    assert res == {
        "hours_child_sum": Decimal("0"),
        "hours_management_sum": Decimal("0"),
        "hours_team_sum": Decimal("0"),
        "hours_misc_sum": Decimal("0"),
        "hours_sum": Decimal("0"),
    }

    # create some data
    emp1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(
        emp1,
        **{
            "date": ["2010-01-01", "2030-01-01"],
            "hours_child": 10,
            "hours_management": 8,
            "hours_team": 6,
            "hours_misc": 4,
        },
    )

    # check outside of contract dates
    res = EmployeeContract.objects.sum_hours(parse("2040-01-01"))
    assert res == {
        "hours_child_sum": Decimal("0"),
        "hours_management_sum": Decimal("0"),
        "hours_team_sum": Decimal("0"),
        "hours_misc_sum": Decimal("0"),
        "hours_sum": Decimal("0"),
    }

    # check during contract dates
    res = EmployeeContract.objects.sum_hours(parse("2020-01-01"))
    assert res == {
        "hours_child_sum": Decimal("10.00"),
        "hours_management_sum": Decimal("8.00"),
        "hours_team_sum": Decimal("6.00"),
        "hours_misc_sum": Decimal("4.00"),
        "hours_sum": Decimal("28.00"),
    }

    # with a second Employee
    emp2 = Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")
    _employeecontract_create(
        emp2,
        **{
            "date": ["2020-01-01", "2030-01-01"],
            "hours_child": 1,
            "hours_management": 2,
            "hours_team": 3,
            "hours_misc": 4,
        },
    )

    # check during date where only first contract is active
    res = EmployeeContract.objects.sum_hours(parse("2015-01-01"))
    assert res == {
        "hours_child_sum": Decimal("10.00"),
        "hours_management_sum": Decimal("8.00"),
        "hours_team_sum": Decimal("6.00"),
        "hours_misc_sum": Decimal("4.00"),
        "hours_sum": Decimal("28.00"),
    }

    # check during date where both contracts for both employees are active
    res = EmployeeContract.objects.sum_hours(parse("2022-01-01"))
    assert res == {
        "hours_child_sum": Decimal("11.00"),
        "hours_management_sum": Decimal("10.00"),
        "hours_team_sum": Decimal("9.00"),
        "hours_misc_sum": Decimal("8.00"),
        "hours_sum": Decimal("38.00"),
    }


@pytest.mark.django_db
def test_employeecontract_sum_hours_group_by_area():
    """
    Check EmployeeContract sum_hours_group_by_area()
    """
    # without any data
    res = EmployeeContract.objects.sum_hours_group_by_area(parse("2020-01-01"))
    assert res.count() == 0

    # create some data
    emp1 = Employee.objects.create(first_name="1", last_name="11", birth_date="2017-10-22")
    _employeecontract_create(
        emp1,
        **{
            "date": ["2010-01-01", "2030-01-01"],
            "hours_child": 10,
            "hours_management": 8,
            "hours_team": 6,
            "hours_misc": 4,
        },
    )

    # check outside of contract data
    res = EmployeeContract.objects.sum_hours_group_by_area(parse("2000-01-01"))
    assert res.count() == 0

    # check inside of contract data
    res = EmployeeContract.objects.sum_hours_group_by_area(parse("2020-01-01"))
    assert list(res) == [{"area": "area1", "hours_sum": Decimal("28.00")}]

    # 2nd employee within the same area
    emp2 = Employee.objects.create(first_name="2", last_name="22", birth_date="2017-10-22")
    _employeecontract_create(
        emp2,
        **{
            "date": ["2021-01-01", "2030-01-01"],
            "hours_child": 10,
            "hours_management": 8,
            "hours_team": 6,
            "hours_misc": 4,
        },
    )

    # check inside of contract data for emp1 only
    res = EmployeeContract.objects.sum_hours_group_by_area(parse("2020-01-01"))
    assert list(res) == [{"area": "area1", "hours_sum": Decimal("28.00")}]

    # check inside of contract data for emp1 and emp2
    res = EmployeeContract.objects.sum_hours_group_by_area(parse("2022-01-01"))
    assert list(res) == [{"area": "area1", "hours_sum": Decimal("56.00")}]

    # 3nd employee within different area
    emp3 = Employee.objects.create(first_name="3", last_name="33", birth_date="2017-10-22")
    area2 = Area.objects.create(name="area2", educational=True)
    _employeecontract_create(
        emp3,
        **{
            "date": ["2021-01-01", "2035-01-01"],
            "hours_child": 1,
            "hours_management": 1,
            "hours_team": 1,
            "hours_misc": 1,
            "area": area2,
        },
    )
    # all employees
    res = EmployeeContract.objects.sum_hours_group_by_area(parse("2022-01-01"))
    assert list(res) == [
        {"area": "area1", "hours_sum": Decimal("56.00")},
        {"area": "area2", "hours_sum": Decimal("4.00")},
    ]

    # only 3rd employee
    res = EmployeeContract.objects.sum_hours_group_by_area(parse("2033-01-01"))
    assert list(res) == [{"area": "area2", "hours_sum": Decimal("4.00")}]
