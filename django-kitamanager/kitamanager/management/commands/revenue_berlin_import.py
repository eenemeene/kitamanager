import os
from django.core.management.base import BaseCommand
from kitamanager.models import RevenueName, RevenueEntry
from kitamanager.berlin import BerlinInvoice
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    help = "Import 'Senatsabrechnung' (invoice) from Berlin/Germany"

    def add_arguments(self, parser):
        parser.add_argument("revenue-name")
        parser.add_argument("file-path")

    def handle(self, *args, **options):
        file_path_list = []
        if os.path.isdir(options["file-path"]):
            file_path_list = [
                os.path.join(options["file-path"], path)
                for path in os.listdir(options["file-path"])
                if path.endswith(".xlsx")
            ]
        elif options["file-path"].endswith(".xlsx"):
            file_path_list = [options["file-path"]]

        # get or create RevenueName
        revenue_name, created = RevenueName.objects.get_or_create(name=options["revenue-name"])

        for file_path in file_path_list:
            invoice = BerlinInvoice(file_path)
            kwargs = dict(name=revenue_name, start=invoice.date, end=invoice.date + relativedelta(months=1))
            defaults = dict(pay=invoice.pay, comment=f"Imported from {os.path.basename(file_path)}")

            re, created = RevenueEntry.objects.update_or_create(defaults, **kwargs)
            if created:
                self.stdout.write(f"{re} created")
            else:
                self.stdout.write(f"{re} updated")
