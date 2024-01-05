import datetime
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
import logging
from kitamanager.models.person import Person, PersonContract, PersonContractManager
from kitamanager.models.employee_payment import EmployeePaymentTable, EmployeePaymentTableEntry
from typing import Optional
from kitamanager import definitions
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.core.validators import MinValueValidator


logger = logging.getLogger(__name__)


class Employee(Person):
    """
    Base data for a Employee
    """

    def get_absolute_url(self):
        return reverse("kitamanager:employee-detail", args=[self.pk])

    def pay_level_next(self, date: datetime.date) -> Optional[datetime.date]:
        """
        When is the next pay level expected on the given date?
        """
        contract = self.contracts.get(date__contains=(date))
        # is the Employee already at the end of the pay levels?
        if contract.pay_level == len(definitions.PAY_LEVEL_BY_YEARS):
            return None

        years_required_for_next = definitions.PAY_LEVEL_BY_YEARS[
            min(len(definitions.PAY_LEVEL_BY_YEARS), contract.pay_level + 1)
        ]
        if self.begin_date:
            return self.begin_date + relativedelta(years=years_required_for_next)
        return None

    def salary(self, date: datetime.date):
        """
        The salary for a given date
        """
        try:
            contract = self.contracts.get(date__contains=(date))
        except EmployeeContract.DoesNotExist:
            return None
        try:
            pay_plan_table = contract.pay_plan.tables.get(date__contains=date)
        except EmployeePaymentTable.DoesNotExist:
            return None
        try:
            pay_plan_table_entry = pay_plan_table.entries.get(
                pay_level=contract.pay_level, pay_group=contract.pay_group
            )
        except EmployeePaymentTableEntry.DoesNotExist:
            return None
        return pay_plan_table_entry.salary * contract.hours_total / pay_plan_table.hours


class EmployeeContractManager(PersonContractManager):
    def sum_hours(self, date: datetime.date):
        """
        Sum of all type of hours at the given date
        """
        return self.by_date(date).aggregate(
            hours_child_sum=models.Sum("hours_child", default=0),
            hours_management_sum=models.Sum("hours_management", default=0),
            hours_team_sum=models.Sum("hours_team", default=0),
            hours_misc_sum=models.Sum("hours_misc", default=0),
            hours_sum=models.Sum("hours_child", default=0)
            + models.Sum("hours_management", default=0)
            + models.Sum("hours_team", default=0)
            + models.Sum("hours_misc", default=0),
        )

    def sum_hours_group_by_area(self, date: datetime.date):
        """
        Sum of all type of hours grouped by area at the given date
        """
        return (
            self.by_date(date)
            .values("area")
            .annotate(
                hours_sum=models.Sum("hours_child", default=0)
                + models.Sum("hours_management", default=0)
                + models.Sum("hours_team", default=0)
                + models.Sum("hours_misc", default=0),
            )
        )

    def sum_salaries(self, date: datetime.date):
        """
        Sum of all salaries for the given date
        """
        salary = Decimal("0")
        for c in self.by_date(date):
            s = c.person.salary(date)
            if s:
                salary += s
        return salary


class EmployeeContract(PersonContract):
    """
    A Employee contract for a specific point in time
    """

    # override person from abstract base model
    person = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="contracts")
    qualification = models.ForeignKey(
        "EmployeeQualification", on_delete=models.CASCADE, help_text=_("qualification the employee has")
    )
    pay_plan = models.ForeignKey("EmployeePaymentPlan", on_delete=models.CASCADE, related_name="pay_plans")
    pay_group = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], help_text=_("pay group"))
    pay_level = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], help_text=_("pay level"))
    hours_child = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("37.0"),
        validators=[MinValueValidator(0)],
        help_text=_("working hours per week (childreen)"),
    )
    hours_management = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(0)],
        help_text=_("working hours per week (management)"),
    )
    hours_team = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("2"),
        validators=[MinValueValidator(0)],
        help_text=_("working hours per week (team)"),
    )
    hours_misc = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(0)],
        help_text=_("working hours per week (miscellaneous)"),
    )

    # default and custom managers
    objects = EmployeeContractManager()

    def __str__(self):
        return f"{self.person}: {self.date} (area: {self.area}, qualification: {self.qualification})"

    def get_absolute_url(self):
        return reverse("kitamanager:employee-detail", args=[self.person.pk])

    @property
    def hours_total(self):
        """
        Sum of the different types of working hours
        """
        return self.hours_child + self.hours_management + self.hours_team + self.hours_misc


class EmployeeQualification(models.Model):
    """
    A qualification used by an EmployeeContract
    """

    name = models.CharField(max_length=255, primary_key=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]
        ordering = ("-name",)
