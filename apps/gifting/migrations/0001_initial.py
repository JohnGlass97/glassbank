# Generated by Django 3.2.9 on 2022-12-24 22:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('banking', '0006_alter_account_firebase'),
    ]

    operations = [
        migrations.CreateModel(
            name='GiftCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('code', models.CharField(default='00271489', max_length=8)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='giftcards_received', to='banking.account')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='giftcards_sent', to='banking.account')),
            ],
        ),
    ]
