import argparse
from django.core.management.base import BaseCommand
from kitamanager.models import ChildPaymentPlan, ChildPaymentTable, ChildPaymentTableEntry

import yaml


class Command(BaseCommand):
    help = "Import child payment tables from a yaml file"

    def add_arguments(self, parser):
        parser.add_argument("paymentplan-name", type=str)
        parser.add_argument("payment-file", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        paymentplan_name = options["paymentplan-name"]
        data = yaml.safe_load(options["payment-file"])

        plan, created = ChildPaymentPlan.objects.get_or_create(name=paymentplan_name)
        self.stdout.write(self.style.SUCCESS(f"Using plan {plan} (newly created? {created})"))

        for el in data:
            defaults_table = dict()
            if el.get("comment"):
                defaults_table["comment"] = el["comment"]
            table, created = ChildPaymentTable.objects.update_or_create(
                plan=plan, start=el["from"], end=el["to"], defaults=defaults_table
            )
            self.stdout.write(self.style.SUCCESS(f"{plan}: Using table >{table}< (newly created? {created})"))

            for entry in el["entries"]:
                for key, value in entry["properties"].items():
                    defaults_entry = dict(pay=value["payment"], requirement=value["requirement"])
                    if value.get("comment"):
                        defaults_entry["comment"] = value["comment"]
                    table_entry, created = ChildPaymentTableEntry.objects.update_or_create(
                        table=table, age=entry["age"], name=key, defaults=defaults_entry
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"{plan}: table {table}: {key}:{value} (newly created? {created})")
                    )
        self.stdout.write(self.style.SUCCESS("Done"))
