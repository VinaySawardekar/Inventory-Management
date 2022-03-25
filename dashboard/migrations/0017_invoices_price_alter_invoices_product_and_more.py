# Generated by Django 4.0.3 on 2022-03-23 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_alter_invoices_invoice_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoices',
            name='price',
            field=models.PositiveBigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='invoices',
            name='product',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='invoices',
            name='staff',
            field=models.CharField(max_length=100, null=True),
        ),
    ]