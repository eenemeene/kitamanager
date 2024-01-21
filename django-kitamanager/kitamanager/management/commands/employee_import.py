import argparse
from django.core.management.base import BaseCommand
from kitamanager.models import Employee, EmployeeContract, EmployeePaymentPlan, Area, EmployeeQualification

import yaml


class Command(BaseCommand):
    help = "Import employee and contracts from a json file which was exported from an older kitamanager version"

    def add_arguments(self, parser):
        parser.add_argument("paymentplan-name", type=str)
        parser.add_argument("employee-file", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        paymentplan_name = options["paymentplan-name"]

        plan = EmployeePaymentPlan.objects.get(name=paymentplan_name)

        data = yaml.safe_load(options["employee-file"])

        for employee in data["mitarbeiter"]:
            e, created = Employee.objects.get_or_create(
                first_name=employee["first_name"],
                last_name=employee["last_name"],
                birth_date=employee["birth_date"],
            )
            print(e, created)
            for c in employee["contracts"]:
                if c["area"] == "Sonstiges":
                    area, created = Area.objects.get_or_create(name=c["area"], defaults=dict(educational=False))
                else:
                    area, created = Area.objects.get_or_create(name=c["area"], defaults=dict(educational=True))
                qualification, created = EmployeeQualification.objects.get_or_create(name=c["qualification"])
                ec, created = EmployeeContract.objects.get_or_create(
                    person=e,
                    start=c["begin"],
                    end=c["end"],
                    area=area,
                    qualification=qualification,
                    hours_child=c["hours_child"],
                    hours_management=c["hours_management"],
                    hours_team=c["hours_team"],
                    hours_misc=c["hours_misc"],
                    pay_plan=plan,
                    pay_group=c["pay_group"],
                    pay_level=c["pay_level"],
                )
                print(ec, created)

        self.stdout.write(self.style.SUCCESS("Done"))
