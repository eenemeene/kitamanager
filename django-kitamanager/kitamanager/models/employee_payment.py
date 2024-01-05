from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from django.core.validators import MinValueValidator
from django.urls import reverse
from decimal import Decimal
from kitamanager.models.common import validate_daterange_not_identical


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
    date = DateRangeField(
        validators=[validate_daterange_not_identical], help_text=_("start/end date for the employee payment table")
    )
    hours = models.DecimalField(max_digits=4, decimal_places=2, default=39.00, help_text=_("weekly working hours"))
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.plan}: {self.date} ({self.hours})"

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_plan_date_overlap",
                expressions=[
                    ("date", RangeOperators.OVERLAPS),
                    ("plan", RangeOperators.EQUAL),
                ],
            ),
        ]
        indexes = [
            models.Index(fields=["date", "hours"]),
        ]
        get_latest_by = ["date"]
        ordering = ("date",)


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
