from django.db import models
from django.utils.translation import gettext_lazy as _


class Area(models.Model):
    """
    A Area where Employees can work and Children can be
    """

    name = models.CharField(max_length=255, help_text=_("name of the area"), primary_key=True)
    educational = models.BooleanField(help_text=_("is this area educational (so an educator, not eg. a cook) ?"))
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (educational: {self.educational})"

    class Meta:
        indexes = [
            models.Index(fields=["name", "educational"]),
        ]
        ordering = ("-name",)
