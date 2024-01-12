import argparse
from django.core.management.base import BaseCommand
from kitamanager.models import EmployeePaymentPlan, EmployeePaymentTable, EmployeePaymentTableEntry

import yaml


class Command(BaseCommand):
    help = "Import employee payment tables from a yaml file"

    def add_arguments(self, parser):
        parser.add_argument("paymentplan-name", type=str)
        parser.add_argument("payment-file", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        paymentplan_name = options["paymentplan-name"]
        data = yaml.safe_load(options["payment-file"])

        plan, created = EmployeePaymentPlan.objects.get_or_create(name=paymentplan_name)
        self.stdout.write(self.style.SUCCESS(f"Using plan {plan} (newly created? {created})"))

        for el in data:
            table, created = EmployeePaymentTable.objects.get_or_create(
                plan=plan, start=el["from"], end=el["to"], hours=el["hours"]
            )
            self.stdout.write(self.style.SUCCESS(f"{plan}: Using table >{table}< (newly created? {created})"))

            for pay_group, value in el["entries"].items():
                for pay_level, salary in el["entries"][pay_group].items():
                    table_entry, created = EmployeePaymentTableEntry.objects.get_or_create(
                        table=table, pay_group=pay_group, pay_level=pay_level, salary=salary
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{plan}: table {table}: {pay_group}/{pay_level}: {salary} (newly created? {created})"
                        )
                    )
        self.stdout.write(self.style.SUCCESS("Done"))
