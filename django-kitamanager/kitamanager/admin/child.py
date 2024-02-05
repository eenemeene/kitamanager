from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from kitamanager.models import (
    ChildContract,
    ChildPaymentTable,
    Area,
)


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

        childpayment_tables = ChildPaymentTable.objects.by_daterange(
            self.cleaned_data["start"], self.cleaned_data["end"]
        ).filter(plan=self.cleaned_data["pay_plan"])
        valid_tags = set()
        for cpt in childpayment_tables:
            for e in list(cpt.entries.values_list("name", flat=True)):
                valid_tags.add(e)
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
    list_display = ["get_child_first_name", "get_child_last_name", "start", "end", "area", "pay_plan", "pay_tags"]
    search_fields = [
        "person__first_name",
        "person__last_name",
    ]
    list_filter = ["area", "pay_tags"]

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
    list_display = ["plan", "start", "end", "comment"]


class ChildPaymentTableEntryAdmin(admin.ModelAdmin):
    list_display = ["table", "age", "name", "pay", "requirement"]
    list_filter = ["table", "name", "age"]
    search_fields = ["name", "pay", "requirement"]
