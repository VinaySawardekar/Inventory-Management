# Generated by Django 4.0.3 on 2022-03-23 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_alter_product_category_invoices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoices',
            name='invoice_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
