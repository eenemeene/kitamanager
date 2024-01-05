import argparse
from django.core.management.base import BaseCommand
from kitamanager.models import Child, ChildContract, ChildPaymentPlan, Area

import yaml


class Command(BaseCommand):
    help = "Import children and contracts from a json file which was exported from an older kitamanager version"

    def add_arguments(self, parser):
        parser.add_argument("paymentplan-name", type=str)
        parser.add_argument("child-file", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        paymentplan_name = options["paymentplan-name"]

        plan = ChildPaymentPlan.objects.get(name=paymentplan_name)

        data = yaml.safe_load(options["child-file"])

        for child in data["kinder"]:
            p, created = Child.objects.get_or_create(
                first_name=child["firstName"],
                last_name=child["lastName"],
                birth_date=child["birthDate"],
                voucher=child["voucher"],
            )
            print(p, created)
            for c in child["contracts"]:
                if c["area"] == "Sonstiges":
                    area, created = Area.objects.get_or_create(name=c["area"], defaults=dict(educational=False))
                else:
                    area, created = Area.objects.get_or_create(name=c["area"], defaults=dict(educational=True))

                pay_tag_list = []
                if c["integrationA"]:
                    pay_tag_list.append("integration a")
                if c["integrationB"]:
                    pay_tag_list.append("integration b")
                if c["qm"]:
                    pay_tag_list.append("qm/mss")
                if c["ndh"]:
                    pay_tag_list.append("ndh")
                if c["carePeriod"] == "Gte":
                    pay_tag_list.append("ganztag erweitert")
                if c["carePeriod"] == "Gt":
                    pay_tag_list.append("ganztag")
                if c["carePeriod"] == "Tz":
                    pay_tag_list.append("teilzeit")
                if c["carePeriod"] == "Ht":
                    pay_tag_list.append("halbtag")

                ec, created = ChildContract.objects.get_or_create(
                    person=p,
                    start=c["begin"],
                    end=c["end"],
                    area=area,
                    pay_plan=plan,
                    pay_tags=pay_tag_list,
                )
                print(ec, created)

        self.stdout.write(self.style.SUCCESS("Done"))
