# Generated by Django 4.0.3 on 2022-03-19 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='visible_to',
            field=models.CharField(max_length=20, null=True),
        ),
    ]