# Generated by Django 3.2.9 on 2021-11-16 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0005_shopitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='firebase',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
    ]
