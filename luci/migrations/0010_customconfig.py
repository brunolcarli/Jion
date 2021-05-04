# Generated by Django 2.2.13 on 2021-05-01 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luci', '0008_auto_20210501_0218'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=100)),
                ('server_name', models.CharField(blank=True, max_length=100, null=True)),
                ('main_channel', models.CharField(blank=True, max_length=35, null=True)),
                ('allow_auto_send_messages', models.BooleanField(default=True)),
                ('filter_offensive_messages', models.BooleanField(default=True)),
                ('allow_learning_from_chat', models.BooleanField(default=True)),
            ],
        ),
    ]
