from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import redirect
from django import forms
from django.core.exceptions import ValidationError
from kitamanager.bankimport import BankAccountEntryImport
from dateutil.relativedelta import relativedelta
from kitamanager.models import (
    BankAccount,
    BankAccountEntry,
)


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ["name"]


def validate_bankaccountentry_import(value):
    try:
        BankAccountEntryImport(value)
    except Exception:
        raise ValidationError(_(f"Can not import file {value}. Wrong format?"))


class BankAccountEntryImportForm(forms.Form):
    file_xls = forms.FileField(validators=[validate_bankaccountentry_import])


class BankAccountEntryAdmin(admin.ModelAdmin):
    list_display = ["bankaccount", "start", "end", "balance"]
    change_list_template = "kitamanager/admin/bankaccountentry_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        # add the import url to be able to import Kontostaende files
        my_urls = [
            path("import/", self._import, name="bankaccountentry-import"),
        ]
        return my_urls + urls

    def _import(self, request):
        context = dict(
            self.admin_site.each_context(request),
        )
        context["title"] = _("Import bank account entries from .xls file")

        if request.method == "POST":
            form = BankAccountEntryImportForm(request.POST, request.FILES)
            if form.is_valid():
                f = form.cleaned_data["file_xls"]
                baei = BankAccountEntryImport(f)
                for account_name, balance in baei.balance.items():
                    ba, created = BankAccount.objects.get_or_create(name=account_name)
                    # we assume here, that the date will be 1 month back
                    kwargs = dict(
                        bankaccount=ba, start=baei.date.date() - relativedelta(months=1), end=baei.date.date()
                    )
                    defaults = dict(balance=balance)
                    baentry, created = BankAccountEntry.objects.update_or_create(defaults, **kwargs)
                    if created:
                        messages.success(request, _(f"bank account entry {baentry} imported successful"))
                    else:
                        messages.success(request, _(f"bank account entry {baentry} updated successful"))

                return redirect(reverse("admin:kitamanager_bankaccountentry_changelist"))
        else:
            form = BankAccountEntryImportForm()
        context["form"] = form
        return TemplateResponse(request, "kitamanager/admin/bankaccountentry_import.html", context)
