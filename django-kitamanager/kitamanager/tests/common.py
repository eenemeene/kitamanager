import pytest
from kitamanager.models import (
    Area,
    Employee,
    EmployeeContract,
    EmployeeQualification,
    EmployeePaymentPlan,
    EmployeePaymentTable,
    EmployeePaymentTableEntry,
    Child,
    ChildContract,
    ChildPaymentPlan,
    ChildPaymentTable,
    ChildPaymentTableEntry,
)


def _employeepaymentplan_create():
    """
    Helper to create EmployeePaymentPlan and related entries
    """
    plan1, _ = EmployeePaymentPlan.objects.get_or_create(name="plan1")
    table1, _ = EmployeePaymentTable.objects.get_or_create(plan=plan1, date=["2020-01-01", "2020-12-31"])
    EmployeePaymentTableEntry.objects.get_or_create(table=table1, pay_group=1, pay_level=1, salary=100)
    EmployeePaymentTableEntry.objects.get_or_create(table=table1, pay_group=1, pay_level=2, salary=200)
    return plan1


def _employeecontract_create(employee, **kwargs):
    """
    Helper to create EmployeeContract DB entries with defaults for testing
    """
    if "area" not in kwargs:
        kwargs["area"], _ = Area.objects.get_or_create(name="area1", educational=True)
    if "qualification" not in kwargs:
        kwargs["qualification"], _ = EmployeeQualification.objects.get_or_create(name="qualification1")
    if "pay_plan" not in kwargs:
        kwargs["pay_plan"] = _employeepaymentplan_create()
    kwargs_defaults = dict(
        person=employee,
        date=["2000-01-01", "2001-01-01"],
    )
    # override/merge kwargs_defaults with given kwargs
    return EmployeeContract.objects.create(**{**kwargs_defaults, **kwargs})


def _childpaymentplan_create():
    """
    Helper to create ChildPaymentPlan and related entries
    """
    plan1, _ = ChildPaymentPlan.objects.get_or_create(name="plan1")
    table1, _ = ChildPaymentTable.objects.get_or_create(plan=plan1, date=["2020-01-01", "2022-01-01"])
    ChildPaymentTableEntry.objects.get_or_create(table=table1, age=[0, 2], name="ganztag", pay=200, requirement=0.1)
    ChildPaymentTableEntry.objects.get_or_create(
        table=table1, age=[0, 2], name="ganztag erweitert", pay=300, requirement=0.1
    )
    # a second table (different date) with a "base" tag
    table2, _ = ChildPaymentTable.objects.get_or_create(plan=plan1, date=["2024-01-01", "2024-02-01"])
    ChildPaymentTableEntry.objects.get_or_create(table=table2, age=[0, 8], name="ganztag", pay=300, requirement=0.2)
    ChildPaymentTableEntry.objects.get_or_create(table=table2, age=[0, 8], name="base", pay=22, requirement=0.33)
    return plan1


def _childcontract_create(child, **kwargs):
    """
    Helper to create ChildContract DB entries with defaults for testing
    """
    if "area" not in kwargs:
        kwargs["area"], _ = Area.objects.get_or_create(name="area1", educational=True)
    if "pay_plan" not in kwargs:
        kwargs["pay_plan"] = _childpaymentplan_create()
    if "pay_tags" not in kwargs:
        kwargs["pay_tags"] = ["ganztag"]
    kwargs_defaults = dict(
        person=child,
        date=["2000-01-01", "2001-01-01"],
    )
    # override/merge kwargs_defaults with given kwargs
    return ChildContract.objects.create(**{**kwargs_defaults, **kwargs})
