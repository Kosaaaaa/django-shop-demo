# Generated by Django 3.1.1 on 2020-09-11 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0010_auto_20200911_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='size',
            name='name',
            field=models.CharField(max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='size',
            name='size_order',
            field=models.PositiveSmallIntegerField(unique=True),
        ),
    ]
