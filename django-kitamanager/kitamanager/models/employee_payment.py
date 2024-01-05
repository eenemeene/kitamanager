from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import RangeOperators, RangeBoundary
from django.contrib.postgres.constraints import ExclusionConstraint
from django.core.validators import MinValueValidator
from django.urls import reverse
from decimal import Decimal
from kitamanager.models.common import DateRange


class EmployeePaymentPlan(models.Model):
    """
    A employee payment plan
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

    def get_absolute_url(self):
        return reverse("kitamanager:employeepayment-detail", args=[self.pk])


class EmployeePaymentTable(models.Model):
    """
    A EmployeePaymentGroup which is related to a single EmployeePayment
    """

    plan = models.ForeignKey("EmployeePaymentPlan", on_delete=models.CASCADE, related_name="tables")
    start = models.DateField(help_text=_("start date for entry"))
    end = models.DateField(help_text=_("end date for entry"))
    hours = models.DecimalField(max_digits=4, decimal_places=2, default=39.00, help_text=_("weekly working hours"))
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.plan}: {self.start} - {self.end} ({self.hours})"

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_exclude_plan_date_overlap",
                expressions=[
                    (
                        DateRange("start", "end", RangeBoundary()),
                        RangeOperators.OVERLAPS,
                    ),
                    ("plan", RangeOperators.EQUAL),
                ],
            ),
        ]
        get_latest_by = ["start"]
        indexes = [
            models.Index(fields=["start", "end", "hours"]),
        ]
        ordering = ["plan", "-start"]


class EmployeePaymentTableEntry(models.Model):
    """
    A EmployeePaymentGroupEntry which is related to a single EmployeePaymentGroup
    """

    table = models.ForeignKey("EmployeePaymentTable", on_delete=models.CASCADE, related_name="entries")
    pay_group = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], help_text=_("pay group"))
    pay_level = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], help_text=_("pay level"))
    salary = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(0)],
        help_text=_("monthly salary"),
    )
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ("-pay_group", "-pay_level")
        constraints = [
            models.UniqueConstraint(
                fields=["table", "pay_group", "pay_level"],
                name="%(app_label)s_%(class)s_table_paygroup_paylevel",
            )
        ]
        indexes = [
            models.Index(fields=["pay_group", "pay_level", "salary"]),
        ]
