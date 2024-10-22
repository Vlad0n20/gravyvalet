# Generated by Django 4.2.7 on 2024-09-17 12:35

from django.db import (
    migrations,
    models,
)

import addon_service.external_service.storage.models


class Migration(migrations.Migration):

    dependencies = [
        ("addon_service", "0003_configuredcitationaddon_root_folder_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="externalstorageservice",
            name="int_supported_features",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[
                    addon_service.external_service.storage.models.validate_supported_features
                ],
            ),
        ),
    ]
