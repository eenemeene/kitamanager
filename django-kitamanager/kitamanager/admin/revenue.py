from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from kitamanager.berlin import BerlinInvoice
from kitamanager.definitions import REVENUE_NAME_BERLIN
from kitamanager.models import RevenueName, RevenueEntry, ChildContract, Child
from dateutil.relativedelta import relativedelta


def validate_berlin_invoice(value):
    try:
        BerlinInvoice(value)
    except Exception:
        raise ValidationError(
            _(f"Can not import file {value}. Is this a valid decrypted .xslx file from the Berliner Senat?")
        )


class BerlinInvoiceImportForm(forms.Form):
    file_xls = forms.FileField(validators=[validate_berlin_invoice])


class RevenueNameAdmin(admin.ModelAdmin):
    list_display = ["name", "comment"]
    search_fields = ["name"]


class RevenueEntryAdmin(admin.ModelAdmin):
    list_display = ["name", "start", "end", "pay", "comment"]
    search_fields = ["name"]
    change_list_template = "kitamanager/admin/revenueentry_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        # add the import url to be able to import BerlinInvoice (Senatsabrechnungen) files
        my_urls = [
            path("import/", self._import, name="revenueentry-berlin-import"),
        ]
        return my_urls + urls

    def _import(self, request):
        context = dict(
            self.admin_site.each_context(request),
        )
        context["title"] = _("Berlin invoice (Senatabrechnung) import from  .xlsx file")

        if request.method == "POST":
            form = BerlinInvoiceImportForm(request.POST, request.FILES)
            if form.is_valid():
                f = form.cleaned_data["file_xls"]
                invoice = BerlinInvoice(f)
                # get or create RevenueName
                revenue_name, created = RevenueName.objects.get_or_create(name=REVENUE_NAME_BERLIN)

                d_start = invoice.date
                d_end = invoice.date + relativedelta(months=1)
                kwargs = dict(name=revenue_name, start=d_start, end=d_end)
                defaults = dict(pay=invoice.pay, comment=f"Imported from {f}")

                re, created = RevenueEntry.objects.update_or_create(defaults, **kwargs)
                # imported! Yeah!
                if created:
                    messages.success(request, _(f"Revenue invoice Berlin {f} imported ({invoice})"))
                else:
                    messages.success(request, _(f"Revenue invoice Berlin {f} updated ({invoice})"))

                # currently available kinder in the DB
                contracts = ChildContract.objects.filter(start__lte=d_start, end__gte=d_end).values(
                    "person__first_name", "person__last_name", "person__voucher"
                )

                children_db = set([f"{c['person__last_name']}, {c['person__first_name']}" for c in contracts])
                children_invoice = set(
                    [f"{c['last_name']}, {c['first_name']}" for voucher, c in invoice.children.items()]
                )
                children_db_not_invoice = sorted(list(children_db.difference(children_invoice)))

                if len(list(children_db_not_invoice)):
                    messages.warning(
                        request,
                        mark_safe(
                            _(
                                "Children in Kitamanager but not in invoice:"
                                f"<br>{'<br>'.join(children_db_not_invoice)}"
                            )
                        ),
                    )

                children_invoice_not_db = sorted(list(children_invoice.difference(children_db)))
                if len(list(children_invoice_not_db)):
                    messages.warning(
                        request,
                        mark_safe(
                            _(
                                "Children in invoice but not in Kitamanager:"
                                f"<br>{'<br>'.join(children_invoice_not_db)}"
                            )
                        ),
                    )

                # take voucher from invoice and put it into DB if Kind exists in DB
                for voucher, c in invoice.children.items():
                    try:
                        child_db = Child.objects.get(first_name=c["first_name"], last_name=c["last_name"])
                    except Child.DoesNotExist:
                        pass
                    else:
                        if child_db.voucher != voucher:
                            messages.success(
                                request,
                                _(
                                    f"Voucher in invoice for {child_db.last_name}, {child_db.first_name}"
                                    f" is {voucher} gut Kitamanager has  {child_db.voucher}. Voucher"
                                    f" updated in Kitamanager to {voucher}"
                                ),
                            )
                            child_db.voucher = voucher
                            child_db.save()

                return redirect(reverse("admin:kitamanager_revenueentry_changelist"))
        else:
            form = BerlinInvoiceImportForm()

        context["form"] = form
        return TemplateResponse(request, "kitamanager/admin/revenueentry_berlin_import.html", context)
