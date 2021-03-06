# Generated by Django 2.2.13 on 2021-01-28 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('luci', '0003_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('global_intention', models.CharField(max_length=25)),
                ('specific_intention', models.CharField(max_length=50)),
                ('text', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='luci.User')),
            ],
        ),
    ]
