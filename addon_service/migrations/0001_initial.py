# Generated by Django 4.2.7 on 2023-11-28 19:41

import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuthorizedStorageAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("default_root_folder", models.CharField(blank=True)),
            ],
            options={
                "verbose_name": "Authorized Storage Account",
                "verbose_name_plural": "Authorized Storage Accounts",
            },
        ),
        migrations.CreateModel(
            name="ExternalCredentials",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("oauth_key", models.CharField(blank=True, null=True)),
                ("oauth_secret", models.CharField(blank=True, null=True)),
                ("refresh_token", models.CharField(blank=True, null=True)),
                ("date_last_refreshed", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "External Credentials",
                "verbose_name_plural": "External Credentials",
            },
        ),
        migrations.CreateModel(
            name="ExternalService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("name", models.CharField()),
            ],
            options={
                "verbose_name": "External Service",
                "verbose_name_plural": "External Services",
            },
        ),
        migrations.CreateModel(
            name="InternalResource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("resource_uri", models.URLField(db_index=True, unique=True)),
            ],
            options={
                "verbose_name": "Internal Resource",
                "verbose_name_plural": "Internal Resources",
            },
        ),
        migrations.CreateModel(
            name="InternalUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("user_uri", models.URLField(db_index=True, unique=True)),
            ],
            options={
                "verbose_name": "Internal User",
                "verbose_name_plural": "Internal Users",
            },
        ),
        migrations.CreateModel(
            name="ExternalStorageService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("max_concurrent_downloads", models.IntegerField()),
                ("max_upload_mb", models.IntegerField()),
                ("auth_uri", models.URLField()),
                (
                    "external_service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="addon_service.externalservice",
                    ),
                ),
            ],
            options={
                "verbose_name": "External Storage Service",
                "verbose_name_plural": "External Storage Services",
            },
        ),
        migrations.CreateModel(
            name="ExternalAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("remote_account_id", models.CharField()),
                ("remote_account_display_name", models.CharField()),
                (
                    "credentials",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="addon_service.externalcredentials",
                    ),
                ),
                (
                    "external_service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="addon_service.externalservice",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="addon_service.internaluser",
                    ),
                ),
            ],
            options={
                "verbose_name": "External Account",
                "verbose_name_plural": "External Accounts",
            },
        ),
        migrations.CreateModel(
            name="ConfiguredStorageAddon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(editable=False)),
                ("modified", models.DateTimeField()),
                ("root_folder", models.CharField()),
                (
                    "authorized_storage_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="addon_service.authorizedstorageaccount",
                    ),
                ),
                (
                    "internal_resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="configured_storage_addons",
                        to="addon_service.internalresource",
                    ),
                ),
            ],
            options={
                "verbose_name": "Configured Storage Addon",
                "verbose_name_plural": "Configured Storage Addons",
            },
        ),
        migrations.AddField(
            model_name="authorizedstorageaccount",
            name="external_account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="addon_service.externalaccount",
            ),
        ),
        migrations.AddField(
            model_name="authorizedstorageaccount",
            name="external_storage_service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="addon_service.externalstorageservice",
            ),
        ),
    ]