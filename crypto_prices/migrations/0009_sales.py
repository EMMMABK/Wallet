# Generated by Django 4.1.3 on 2023-07-22 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crypto_prices', '0008_remove_purchase_amount_usd'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto_prices.cryptoprice')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
