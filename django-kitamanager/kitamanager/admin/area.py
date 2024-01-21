from django.contrib import admin


class AreaAdmin(admin.ModelAdmin):
    list_display = ["name", "educational"]
    list_filter = ["educational"]
