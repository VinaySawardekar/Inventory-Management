# Generated by Django 4.0.3 on 2022-03-29 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_remove_invoices_unique_id_invoices_temp_id_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoices',
            name='temp_id',
            field=models.IntegerField(null=True),
        ),
    ]