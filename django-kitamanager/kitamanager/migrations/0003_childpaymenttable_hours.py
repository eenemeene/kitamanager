# Generated by Django 5.0.1 on 2024-01-26 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kitamanager", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="childpaymenttable",
            name="hours",
            field=models.DecimalField(
                decimal_places=2,
                default=39.4,
                help_text="weekly working hours for full time",
                max_digits=4,
            ),
        ),
    ]
