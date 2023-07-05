# Generated by Django 4.1.3 on 2023-07-05 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_prices', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cryptoprice',
            name='timestamp',
        ),
        migrations.AlterField(
            model_name='cryptoprice',
            name='price',
            field=models.DecimalField(decimal_places=4, max_digits=12),
        ),
        migrations.AlterField(
            model_name='cryptoprice',
            name='symbol',
            field=models.CharField(max_length=10),
        ),
    ]
