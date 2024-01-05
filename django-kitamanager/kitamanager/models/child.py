import datetime
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
import logging
from kitamanager.models.person import Person, PersonContract, PersonContractManager
from kitamanager.models.child_payment import ChildPaymentTable, ChildPaymentTableEntry
from typing import Optional
from kitamanager import definitions
from dateutil.relativedelta import relativedelta
from decimal import Decimal


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
        return f"{self.person}: {self.date} (area: {self.area})"

    def get_absolute_url(self):
        return reverse("kitamanager:child-detail", args=[self.person.pk])

    def count_group_by_pay_tags(self, date: datetime.date):
        """
        group the number of EmployeeContract for a given date by pay_tags
        """
        return self.by_date(date).values("pay_tags").annotate(total=models.Count("pay_tags"))

    def payment(self, date: datetime.date):
        """
        The payment for the given contract
        """
        if date < self.date.lower or date >= self.date.upper:
            raise ValueError(f"child payment for date {date} and contract date {self.date} invalid. dates do not match")

        # implicitly assume that every child also has the "base" tag
        pay_tags_with_base = self.pay_tags + ["base"]
        qs = ChildPaymentTableEntry.objects.filter(
            table__plan=self.pay_plan,
            table__date__contains=date,
            age__contains=self.person.age(date),
            name__in=pay_tags_with_base,
        )
        return qs.aggregate(models.Sum("pay"))["pay__sum"]

    def requirement(self, date: datetime.date):
        """
        The requirement for the given contract
        """
        if date < self.date.lower or date >= self.date.upper:
            raise ValueError(
                f"child requirement for date {date} and contract date {self.date} invalid. dates do not match"
            )

        # implicitly assume that every child also has the "base" tag
        pay_tags_with_base = self.pay_tags + ["base"]
        qs = ChildPaymentTableEntry.objects.filter(
            table__plan=self.pay_plan,
            table__date__contains=date,
            age__contains=self.person.age(date),
            name__in=pay_tags_with_base,
        )
        return qs.aggregate(models.Sum("requirement"))["requirement__sum"]
