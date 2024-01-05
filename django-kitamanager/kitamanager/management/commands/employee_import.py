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
                first_name=employee["firstName"],
                last_name=employee["lastName"],
                birth_date=employee["birthDate"],
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
                    hours_child=c["hoursChild"],
                    hours_management=c["hoursManagement"],
                    hours_team=c["hoursTeam"],
                    hours_misc=c["hoursMisc"],
                    pay_plan=plan,
                    pay_group=c["payGroup"],
                    pay_level=c["payLevel"],
                )
                print(ec, created)

        self.stdout.write(self.style.SUCCESS("Done"))
