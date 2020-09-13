# Generated by Django 3.1.1 on 2020-09-10 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_auto_20200909_2240'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=100, unique=True)),
                ('price', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-start_date',)},
        ),
        migrations.AlterModelOptions(
            name='sizesvariations',
            options={'ordering': ('product', 'size__size_order'), 'verbose_name_plural': 'Sizes Variations'},
        ),
        migrations.AlterField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='cart.coupon'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(default=0, help_text='Please type price in integer eq. 12.50 PLN -> 1250 PLN'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sale_price',
            field=models.IntegerField(blank=True, help_text='Please type price in integer eq. 12.50 PLN -> 1250 PLN', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cart.shippingmethod'),
        ),
    ]