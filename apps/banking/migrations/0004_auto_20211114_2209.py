# Generated by Django 3.2.9 on 2021-11-14 22:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0003_auto_20211114_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='firebase',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='balance',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='epoch',
            field=models.IntegerField(null=True),
        ),
        migrations.CreateModel(
            name='MoneyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('reference', models.CharField(max_length=100)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='requests_received', to='banking.account')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='requests_sent', to='banking.account')),
            ],
        ),
    ]
