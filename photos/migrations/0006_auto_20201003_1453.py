# Generated by Django 3.1.1 on 2020-10-03 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0005_auto_20201003_1328'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_timestamp']},
        ),
    ]
