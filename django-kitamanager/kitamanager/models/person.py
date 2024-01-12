import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import RangeOperators, RangeBoundary
from django.contrib.postgres.constraints import ExclusionConstraint
from django.utils.translation import gettext_lazy as _
from kitamanager.models.common import DateRange
from typing import Optional


class PersonManager(models.Manager):
    """
    Custom Manager for the Person model
    """

    def by_date(self, date: datetime.date):
        """
        All person contracts at the given date
        :param date: the date
        :type date: datetime.date
        """
        return self.filter(contracts__start__lte=date, contracts__end__gt=date)

    def future(self, date: datetime.date):
        """
        All person contracts in the future (compared by the given date)
        :param date: the date
        :type date: datetime.date
        """
        return (
            self.prefetch_related("contracts")
            .annotate(start_min=models.Min("contracts__start"))
            .filter(start_min__gt=date)
        )


class Person(models.Model):
    """
    Abstract base model for a person
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    comment = models.TextField(blank=True, help_text=_("optional comment"))

    # default and custom managers
    objects = PersonManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "birth_date"],
                name="%(app_label)s_%(class)s_first_name_last_name_birth_date",
            )
        ]

    @property
    def begin_date(self) -> Optional[datetime.date]:
        """
        The lowest date from any PersonContract
        """
        c_min = self.contracts.aggregate(min=models.Min("start"))
        return c_min.get("min", None)

    def age(self, d: datetime.date) -> int:
        """
        The Person age for a given date
        """
        return d.year - self.birth_date.year - ((d.month, d.day) < (self.birth_date.month, self.birth_date.day))


class PersonContractManager(models.Manager):
    """
    Custom Manager for the PersonContract model
    """

    def by_date(self, date: datetime.date):
        """
        All person contracts at the given date
        :param date: the date
        :type date: datetime.date
        """
        return self.select_related("person", "area").filter(start__lte=date, end__gt=date)

    def count_group_by_area(self, date: datetime.date):
        """
        group the number of EmployeeContract for a given date by area
        """
        return self.by_date(date).values("area").annotate(total=models.Count("area"))


class PersonContract(models.Model):
    """
    Abstract base model for a person contract
    """

    person = models.ForeignKey("Person", on_delete=models.CASCADE, related_name="contracts")
    start = models.DateField(help_text=_("start date for the contract"))
    end = models.DateField(help_text=_("end date for the contract"))
    area = models.ForeignKey("Area", on_delete=models.CASCADE, help_text=_("area where the person is"))

    # default and custom managers
    objects = PersonContractManager()

    class Meta:
        abstract = True
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_exclude_person_start_end_overlap",
                expressions=[
                    (
                        DateRange("start", "end", RangeBoundary()),
                        RangeOperators.OVERLAPS,
                    ),
                    ("person", RangeOperators.EQUAL),
                ],
            ),
        ]
        get_latest_by = ["start"]
        ordering = ["person", "start"]

    def __str__(self):
        return f"{self.person}: {self.start} - {self.end} (area: {self.area}"

    def clean(self):
        # don't allow start be >= end
        if self.start >= self.end:
            raise ValidationError({"start": _("start date can not be greater or equal than end date")})
