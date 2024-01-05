import datetime
from django.db import models
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from django.utils.translation import gettext_lazy as _
from dateutil.parser import parse
from psycopg2.extras import DateRange
from dateutil.relativedelta import relativedelta
from typing import Optional
from kitamanager.models.common import validate_daterange_not_identical


class Person(models.Model):
    """
    Abstract base model for a person
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    comment = models.TextField(blank=True, help_text=_("pptional comment"))

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
        c_min = self.contracts.aggregate(date_min=models.Min(models.functions.Lower("date")))
        return c_min.get("date_min", None)

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
        return self.select_related("person", "area").filter(date__contains=(date))

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
    date = DateRangeField(validators=[validate_daterange_not_identical], help_text=_("start/end date for the contract"))
    area = models.ForeignKey("Area", on_delete=models.CASCADE, help_text=_("area where the person is"))

    # default and custom managers
    objects = PersonContractManager()

    def __str__(self):
        return f"{self.person}: {self.date} (area: {self.area}"

    class Meta:
        abstract = True
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_person_date_overlap",
                expressions=[
                    ("date", RangeOperators.OVERLAPS),
                    ("person", RangeOperators.EQUAL),
                ],
            ),
        ]
        get_latest_by = ["date"]
        ordering = (
            "person",
            "date",
        )
