import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import RangeOperators, RangeBoundary
from django.contrib.postgres.constraints import ExclusionConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from kitamanager.models.common import DateRange


class ChildPaymentPlan(models.Model):
    """
    A child payment plan
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
        return reverse("kitamanager:childpayment-detail", args=[self.pk])


class ChildPaymentTableManager(models.Manager):
    """
    Custom Manager for the ChildPaymentTable model
    """

    def by_daterange(self, start: datetime.date, end: datetime.date):
        """
        Filter tables for the plan by date range
        :param start: the start date (included in the result)
        :type start: datetime.date
        :param end: the end date (excluded in the result)
        :type end: datetime.date

        """
        return self.filter(start__lte=end, end__gt=start)


class ChildPaymentTable(models.Model):
    """
    A ChildPaymentTable which is related to a single ChildPaymentPlan
    """

    plan = models.ForeignKey("ChildPaymentPlan", on_delete=models.CASCADE, related_name="tables")
    start = models.DateField(help_text=_("start date"))
    end = models.DateField(help_text=_("end date"))
    hours = models.DecimalField(
        max_digits=4, decimal_places=2, default=39.40, help_text=_("weekly working hours for full time")
    )
    comment = models.TextField(blank=True)

    # default and custom managers
    objects = ChildPaymentTableManager()

    def __str__(self):
        return f"{self.plan}: {self.start} - {self.end}"

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_exclude_plan_start_date_overlap",
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
            models.Index(fields=["start", "end"]),
        ]
        ordering = ["plan", "-start"]


class ChildPaymentTableEntry(models.Model):
    """
    A ChildPaymentTableEntry which is related to a single ChildPaymentEntry
    """

    table = models.ForeignKey("ChildPaymentTable", on_delete=models.CASCADE, related_name="entries")
    age_start = models.PositiveSmallIntegerField(
        help_text=_("age start (in years) range for this property"),
        validators=[MinValueValidator(0), MaxValueValidator(8)],
    )
    age_end = models.PositiveSmallIntegerField(
        help_text=_("age end (in years) range for this property"),
        validators=[MinValueValidator(0), MaxValueValidator(8)],
    )
    name = models.CharField(max_length=255, help_text=_("property name"))
    pay = models.DecimalField(
        max_digits=10, decimal_places=2, help_text=_("imcoming pay (in Euro) to get for this property")
    )
    requirement = models.DecimalField(
        max_digits=10, decimal_places=3, help_text=_("required employees in % (eg. 0.5 means half a person)")
    )
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ("table", "age_start", "age_end", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["table", "age_start", "age_end", "name"],
                name="%(app_label)s_%(class)s_table_age_start_age_end_name",
            )
        ]
        indexes = [
            models.Index(fields=["age_start", "age_end", "name", "pay", "requirement"]),
        ]

    def __str__(self):
        return (
            f"{self.table}: age:{self.age_start}-{self.age_end}, "
            f"name:{self.name}, pay:{self.pay}, req:{self.requirement}"
        )
