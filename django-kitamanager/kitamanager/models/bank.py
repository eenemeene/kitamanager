import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from typing import Dict
from decimal import Decimal
from kitamanager.models.common import validate_daterange_not_identical


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
        return self.select_related("bankaccount").filter(date__contains=date)

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
    date = DateRangeField(validators=[validate_daterange_not_identical], help_text=_("start/end date for entry"))
    balance = models.DecimalField(help_text=_("bank account balance"), max_digits=10, decimal_places=2)

    # default and custom managers
    objects = BankAccountEntryManager()

    def __str__(self):
        return f"{self.bankaccount.name}: {self.date} ({self.balance})"

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="%(app_label)s_%(class)s_bankaccount_date_overlap",
                expressions=[
                    ("date", RangeOperators.OVERLAPS),
                    ("bankaccount", RangeOperators.EQUAL),
                ],
            ),
        ]
        indexes = [
            models.Index(fields=["date", "balance"]),
        ]
        ordering = ("date",)
