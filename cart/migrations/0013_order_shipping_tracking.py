# Generated by Django 3.1.1 on 2020-09-13 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0012_auto_20200911_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_tracking',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
