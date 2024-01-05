from django.contrib import admin
from django.contrib import messages
from django.contrib.postgres.fields import DateRangeField
from django.contrib.postgres.forms import RangeWidget
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import redirect
from django import forms
from django.core.exceptions import ValidationError
from kitamanager.bankimport import BankAccountEntryImport
from dateutil.relativedelta import relativedelta
from django.forms import ModelForm
from kitamanager.models import (
    Employee,
    EmployeeContract,
    EmployeeQualification,
    EmployeePaymentPlan,
    EmployeePaymentTable,
    EmployeePaymentTableEntry,
    Child,
    ChildContract,
    ChildPaymentPlan,
    ChildPaymentTable,
    ChildPaymentTableEntry,
    Area,
    BankAccount,
    BankAccountEntry,
)


class AreaAdmin(admin.ModelAdmin):
    list_display = ["name", "educational"]
    list_filter = ["educational"]


class EmployeeQualificationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


class EmployeeContractAdmin(admin.ModelAdmin):
    list_display = [
        "get_employee_first_name",
        "get_employee_last_name",
        "date",
        "area",
        "qualification",
        "pay_plan",
        "pay_group",
        "pay_level",
        "hours_child",
        "hours_management",
        "hours_team",
        "hours_misc",
    ]
    list_filter = ["area", "qualification", "pay_plan"]
    search_fields = ["person__first_name", "person__last_name"]
    formfield_overrides = {
        DateRangeField: {"widget": RangeWidget(admin.widgets.AdminDateWidget)},
    }

    @admin.display(ordering="person__first_name", description=_("first name"))
    def get_employee_first_name(self, obj):
        return obj.person.first_name

    @admin.display(ordering="person__last_name", description=_("last name"))
    def get_employee_last_name(self, obj):
        return obj.person.last_name


class EmployeeContractInline(admin.TabularInline):
    model = EmployeeContract
    extra = 1
    formfield_overrides = {
        DateRangeField: {"widget": RangeWidget(admin.widgets.AdminDateWidget)},
    }


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "birth_date"]
    search_fields = ["first_name", "last_name"]
    inlines = [
        EmployeeContractInline,
    ]


class EmployeePaymentPlanAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class EmployeePaymentTableAdmin(admin.ModelAdmin):
    list_display = ["plan", "date", "hours"]


class EmployeePaymentTableEntryAdmin(admin.ModelAdmin):
    list_display = ["table", "pay_group", "pay_level", "salary"]


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
    list_display = ["bankaccount", "date", "balance"]
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
                    kwargs = dict(bankaccount=ba, date=[baei.date.date() - relativedelta(months=1), baei.date.date()])
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


class ChildContractForm(ModelForm):
    def clean_area(self):
        # make sure only educational areas can be selected for a child
        if self.cleaned_data["area"].educational is not True:
            raise ValidationError(
                _("area %(area)s can not be selected for a child" % {"area": self.cleaned_data["area"].name})
            )
        else:
            return self.cleaned_data["area"]

    def clean_pay_tags(self):
        # make sure only tags from the selected pay_plan for the given date are used
        childpayment_table = (
            self.cleaned_data["pay_plan"].tables.filter(date__overlap=self.cleaned_data["date"]).latest()
        )
        valid_tags = set(childpayment_table.entries.values_list("name", flat=True))
        diff = set(self.cleaned_data["pay_tags"]).difference(valid_tags)
        if diff:
            raise ValidationError(
                _(
                    "The pay tags '%(invalid_tags)s' are not valid. valid tags are '%(valid_tags)s'"
                    % {"invalid_tags": ", ".join(diff), "valid_tags": ", ".join(valid_tags)}
                )
            )
        else:
            return self.cleaned_data["pay_tags"]


class ChildContractAdmin(admin.ModelAdmin):
    form = ChildContractForm
    list_display = ["get_child_first_name", "get_child_last_name", "date", "area", "pay_plan", "pay_tags"]
    list_filter = ["area", "pay_tags"]
    formfield_overrides = {
        DateRangeField: {"widget": RangeWidget(admin.widgets.AdminDateWidget)},
    }

    @admin.display(ordering="person__first_name", description=_("first name"))
    def get_child_first_name(self, obj):
        return obj.person.first_name

    @admin.display(ordering="person__last_name", description=_("last name"))
    def get_child_last_name(self, obj):
        return obj.person.last_name

    def render_change_form(self, request, context, *args, **kwargs):
        # only show educational areas for childs
        context["adminform"].form.fields["area"].queryset = Area.objects.filter(educational=True)
        return super(ChildContractAdmin, self).render_change_form(request, context, *args, **kwargs)


class ChildContractInline(admin.TabularInline):
    model = ChildContract
    form = ChildContractForm
    extra = 1
    formfield_overrides = {
        DateRangeField: {"widget": RangeWidget(admin.widgets.AdminDateWidget)},
    }


class ChildAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "birth_date", "voucher"]
    search_fields = ["first_name", "last_name", "voucher"]
    inlines = [
        ChildContractInline,
    ]


class ChildPaymentPlanAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class ChildPaymentTableAdmin(admin.ModelAdmin):
    list_display = ["plan", "date", "comment"]


class ChildPaymentTableEntryAdmin(admin.ModelAdmin):
    list_display = ["table", "age", "name", "pay", "requirement"]
    list_filter = ["table", "name", "age"]
    search_fields = ["name", "pay", "requirement"]


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeContract, EmployeeContractAdmin)
admin.site.register(EmployeeQualification, EmployeeQualificationAdmin)
admin.site.register(EmployeePaymentPlan, EmployeePaymentPlanAdmin)
admin.site.register(EmployeePaymentTable, EmployeePaymentTableAdmin)
admin.site.register(EmployeePaymentTableEntry, EmployeePaymentTableEntryAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(ChildContract, ChildContractAdmin)
admin.site.register(ChildPaymentPlan, ChildPaymentPlanAdmin)
admin.site.register(ChildPaymentTable, ChildPaymentTableAdmin)
admin.site.register(ChildPaymentTableEntry, ChildPaymentTableEntryAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(BankAccountEntry, BankAccountEntryAdmin)
