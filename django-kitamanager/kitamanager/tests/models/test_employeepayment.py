import pytest
import datetime
from django.db.utils import IntegrityError
from dateutil.parser import parse

from kitamanager.models import EmployeePaymentPlan, EmployeePaymentTable, EmployeePaymentTableEntry


@pytest.mark.django_db
def test_employeepaymentplan_create():
    """
    Create a single EmployeePaymentPlan
    """
    EmployeePaymentPlan.objects.create(name="plan1")

    # 2nd one with different name should work
    EmployeePaymentPlan.objects.create(name="plan2")

    # 2nd one with same name is not allowed
    with pytest.raises(IntegrityError):
        EmployeePaymentPlan.objects.create(name="plan1")


@pytest.mark.django_db
def test_employeepaymenttable_create():
    """
    Create EmployeePaymentTable's
    """
    p1 = EmployeePaymentPlan.objects.create(name="plan1")
    p2 = EmployeePaymentPlan.objects.create(name="plan2")

    EmployeePaymentTable.objects.create(plan=p1, date=["2020-01-01", "2020-12-31"])
    EmployeePaymentTable.objects.create(plan=p1, date=["2021-01-01", "2021-12-31"])

    # same tables, but for the other plan should work
    EmployeePaymentTable.objects.create(plan=p2, date=["2020-01-01", "2020-12-31"])
    EmployeePaymentTable.objects.create(plan=p2, date=["2021-01-01", "2021-12-31"])

    # overlapping date should not work
    with pytest.raises(IntegrityError):
        EmployeePaymentTable.objects.create(plan=p2, date=["2021-06-01", "2023-12-31"])


@pytest.mark.django_db
def test_employeepaymenttableentry_create():
    """
    Create EmployeePaymentTable's
    """
    p1 = EmployeePaymentPlan.objects.create(name="plan1")
    p2 = EmployeePaymentPlan.objects.create(name="plan2")

    t11 = EmployeePaymentTable.objects.create(plan=p1, date=["2020-01-01", "2020-12-31"])
    t12 = EmployeePaymentTable.objects.create(plan=p1, date=["2021-01-01", "2021-12-31"])

    # same tables, but for the other plan should work
    t21 = EmployeePaymentTable.objects.create(plan=p2, date=["2020-01-01", "2020-12-31"])
    t22 = EmployeePaymentTable.objects.create(plan=p2, date=["2021-01-01", "2021-12-31"])

    # same group/level/salary should work in different tables
    EmployeePaymentTableEntry.objects.create(table=t11, pay_group=1, pay_level=1, salary=1000)
    EmployeePaymentTableEntry.objects.create(table=t12, pay_group=1, pay_level=1, salary=1000)
    EmployeePaymentTableEntry.objects.create(table=t21, pay_group=1, pay_level=1, salary=1000)
    EmployeePaymentTableEntry.objects.create(table=t22, pay_group=1, pay_level=1, salary=1000)

    # different group/level/salary should work in the same table
    EmployeePaymentTableEntry.objects.create(table=t11, pay_group=1, pay_level=2, salary=1000)

    # same group/level with different salary in the same table shouldn't work
    with pytest.raises(IntegrityError):
        EmployeePaymentTableEntry.objects.create(table=t11, pay_group=1, pay_level=2, salary=2000)
