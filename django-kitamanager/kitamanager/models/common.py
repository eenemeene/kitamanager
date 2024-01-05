from django.contrib.postgres.fields import DateRangeField
from django.db.models import Func


# see https://docs.djangoproject.com/en/5.0/ref/contrib/postgres/constraints/
class DateRange(Func):
    function = "DATERANGE"
    output_field = DateRangeField()
