from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_daterange_not_identical(value):
    if value.lower == value.upper:
        raise ValidationError(
            _("lower and upper date (%(value)s) can not be identical"),
            params={"value": value},
        )
