# Generated by Django 2.2.13 on 2021-05-04 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luci', '0010_customconfig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='quote',
            field=models.BinaryField(),
        ),
    ]
