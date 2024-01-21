from django.contrib import admin


class RevenueNameAdmin(admin.ModelAdmin):
    list_display = ["name", "comment"]
    search_fields = ["name"]


class RevenueEntryAdmin(admin.ModelAdmin):
    list_display = ["name", "start", "end", "pay", "comment"]
    search_fields = ["name"]
