import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import RangeOperators, RangeBoundary
from django.contrib.postgres.constraints import ExclusionConstraint
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from typing import Dict
from decimal import Decimal
from kitamanager.models.common import DateRange


class BankAccount(models.Model):
    """
    A bank account
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


class BankAccountEntryManager(models.Manager):
    def by_date(self, date: datetime.date):
        """
        All bank account entries at the given date
        :param date: the date
        :type date: datetime.date
        """
        return self.select_related("bankaccount").filter(start__lte=date, end__gt=date)

    def sum_balance(self, date: datetime.date):
        """
        Sum of all balances for all bank accounts for a given date
        """
        return self.by_date(date).aggregate(balance_sum=models.Sum("balance", default=0))

    def sum_balance_by_month(self, date_start: datetime.date, date_end: datetime.date):
        """
        Sum of all balances for all bank accounts for each month between date_start and date_end
        """
        data: Dict[datetime.date, Decimal] = dict()
        d: datetime.date = date_start
        while d <= date_end:
            data[d] = self.sum_balance(d)["balance_sum"]
            d = d + relativedelta(months=1)
        return data


class BankAccountEntry(models.Model):
    """
    A BankAccountEntry
    """

    bankaccount = models.ForeignKey("BankAccount", on_delete=models.CASCADE, related_name="entries")
    start = models.DateField(help_text=_("start date for entry"))
    end = models.DateField(help_text=_("end date for entry"))
    balance = models.DecimalField(help_text=_("bank account balance"), max_digits=10, decimal_places=2)

    # default and custom managers
    objects = BankAccountEntryManager()

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_exclude_bankaccount_start_end_overlap",
                expressions=[
                    (
                        DateRange("start", "end", RangeBoundary()),
                        RangeOperators.OVERLAPS,
                    ),
                    ("bankaccount", RangeOperators.EQUAL),
                ],
            ),
        ]
        get_latest_by = ["start"]
        indexes = [
            models.Index(fields=["start", "end", "balance"]),
        ]
        ordering = (
            "bankaccount",
            "-start",
        )

    def __str__(self):
        return f"{self.bankaccount.name}: {self.start} - {self.end} ({self.balance})"

    def clean(self):
        # don't allow start be >= end
        if self.start >= self.end:
            raise ValidationError({"start": _("start date can not be greater or equal than end date")})
