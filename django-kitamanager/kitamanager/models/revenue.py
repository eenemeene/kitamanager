import datetime
from django.db import models
from django.contrib.postgres.fields import RangeOperators, RangeBoundary
from django.contrib.postgres.constraints import ExclusionConstraint
from django.utils.translation import gettext_lazy as _
from kitamanager.models.common import DateRange


class RevenueName(models.Model):
    """
    A Revenue Name
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


class RevenueEntryManager(models.Manager):
    """
    Custom Manager for the RevenueEntry model
    """

    def by_date(self, date: datetime.date):
        """
        All entries at the given date
        :param date: the date
        :type date: datetime.date
        """
        return self.select_related("name").filter(start__lte=date, end__gt=date)


class RevenueEntry(models.Model):
    """
    A RevenueEntry which is related to a single RevenueName
    """

    name = models.ForeignKey("RevenueName", on_delete=models.CASCADE, related_name="entries")
    start = models.DateField(help_text=_("start date"))
    end = models.DateField(help_text=_("end date"))
    pay = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("pay (in Euro)"))
    comment = models.TextField(blank=True)

    # default and custom managers
    objects = RevenueEntryManager()

    def __str__(self):
        return f"{self.name}: {self.start} - {self.end}"

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_exclude_name_start_date_overlap",
                expressions=[
                    (
                        DateRange("start", "end", RangeBoundary()),
                        RangeOperators.OVERLAPS,
                    ),
                    ("name", RangeOperators.EQUAL),
                ],
            ),
        ]
        get_latest_by = ["start"]
        indexes = [
            models.Index(fields=["start", "end"]),
        ]
        ordering = ["name", "-start"]
