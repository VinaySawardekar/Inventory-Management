# Generated by Django 4.0.3 on 2022-03-29 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_invoices_price_alter_invoices_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoices',
            name='unique_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]