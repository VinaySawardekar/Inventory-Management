# Generated by Django 4.0.3 on 2022-03-16 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_category_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='mobile_no',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='category',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
