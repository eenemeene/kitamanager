from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from kitamanager.models import (
    EmployeeContract,
)


class EmployeeQualificationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


class EmployeeContractAdmin(admin.ModelAdmin):
    list_display = [
        "get_employee_first_name",
        "get_employee_last_name",
        "start",
        "end",
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

    @admin.display(ordering="person__first_name", description=_("first name"))
    def get_employee_first_name(self, obj):
        return obj.person.first_name

    @admin.display(ordering="person__last_name", description=_("last name"))
    def get_employee_last_name(self, obj):
        return obj.person.last_name


class EmployeeContractInline(admin.TabularInline):
    model = EmployeeContract
    extra = 1


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
    list_display = ["plan", "start", "end", "hours"]


class EmployeePaymentTableEntryAdmin(admin.ModelAdmin):
    list_display = ["table", "pay_group", "pay_level", "salary"]
