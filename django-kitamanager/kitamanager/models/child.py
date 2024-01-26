import datetime
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
import logging
from kitamanager.models.person import Person, PersonContract, PersonContractManager
from kitamanager.models.child_payment import ChildPaymentTable, ChildPaymentTableEntry
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from typing import Dict, List


logger = logging.getLogger(__name__)


class Child(Person):
    """
    Base data for a Child
    """

    voucher = models.CharField(max_length=255, help_text=_("the voucher identifier"))

    def get_absolute_url(self):
        return reverse("kitamanager:child-detail", args=[self.pk])


class ChildContractManager(PersonContractManager):
    def sum_payments(self, date: datetime.date):
        """
        Sum of all payments for the given date
        """
        payments = Decimal("0")
        for c in self.by_date(date):
            p = c.payment(date)
            if p:
                payments += p
        return payments

    def sum_requirements(self, date: datetime.date):
        """
        Sum of all requirements for the given date
        That sum is the full time positions per week
        :return: a tuple with sum of requirements and sum of requirements in h/week
            full time work
        :rtype: Tuple[Decimal, Decimal]
        """
        requirements = Decimal("0")
        requirements_hours_per_week = Decimal("0")
        for c in self.by_date(date):
            r = c.requirement(date)
            if r:
                requirements += r[0]
                requirements_hours_per_week += r[0] * r[1]
        return requirements, requirements_hours_per_week

    def count_by_month(self, from_dt: datetime.date, to_dt: datetime.date) -> Dict[int, List[int]]:
        """
        Children count by month
        param from_dt: the date to start with (date included)
        type from_dt: datetime.date
        param to_dt: the date to end with (date excluded)
        type from_dt: datetime.date
        """
        data = dict()  # type: Dict[int, List[int]]
        current = from_dt
        while current < to_dt:
            # total amount of children for that current date
            children_total = self.by_date(current).count()
            if not data.get(current.year):
                data[current.year] = []
            data[current.year].append(children_total)
            current = current + relativedelta(months=1)
        return data


class ChildContract(PersonContract):
    """
    A ChildContract for a specific point in time
    """

    # override person from abstract base model
    person = models.ForeignKey("Child", on_delete=models.CASCADE, related_name="contracts")
    pay_plan = models.ForeignKey("ChildPaymentPlan", on_delete=models.CASCADE, related_name="pay_plans")
    pay_tags = ArrayField(
        models.CharField(max_length=255),
        help_text=_("list of comma separated payment properties. Those must match the payment plan"),
    )

    # default and custom managers
    objects = ChildContractManager()

    def __str__(self):
        return f"{self.person}: {self.start} - {self.end} (area: {self.area})"

    def get_absolute_url(self):
        return reverse("kitamanager:child-detail", args=[self.person.pk])

    def payment(self, date: datetime.date):
        """
        The payment for the given contract
        """
        if date < self.start or date >= self.end:
            raise ValueError(
                f"child payment for date {date} and contract start/end "
                f"{self.start} - {self.end} invalid. dates do not match"
            )

        # implicitly assume that every child also has the "base" tag
        pay_tags_with_base = self.pay_tags + ["base"]
        qs = ChildPaymentTableEntry.objects.filter(
            table__plan=self.pay_plan,
            table__start__lte=date,
            table__end__gt=date,
            age__contains=self.person.age(date),
            name__in=pay_tags_with_base,
        )
        return qs.aggregate(models.Sum("pay"))["pay__sum"]

    def requirement(self, date: datetime.date):
        """
        The requirement for the given contract
        :return: Either None or a tuple with the sum for requirements and the hours for
            full time work
        :rtype: Optional[Tuple[Decimal, Decimal]]
        """
        if date < self.start or date >= self.end:
            raise ValueError(
                f"child requirement for date {date} and contract start/end"
                f"{self.start} - {self.end} invalid. dates do not match"
            )

        # implicitly assume that every child also has the "base" tag
        pay_tags_with_base = self.pay_tags + ["base"]
        try:
            table = ChildPaymentTable.objects.get(plan=self.pay_plan, start__lte=date, end__gt=date)
        except ChildPaymentTable.DoesNotExist:
            return None

        qs = ChildPaymentTableEntry.objects.filter(
            table=table,
            age__contains=self.person.age(date),
            name__in=pay_tags_with_base,
        )
        sum = qs.aggregate(models.Sum("requirement"))["requirement__sum"]
        if not sum:
            return None

        return (sum, table.hours)
