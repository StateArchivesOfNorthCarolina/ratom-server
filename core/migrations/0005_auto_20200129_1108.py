# Generated by Django 2.2.8 on 2020-01-29 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200127_1954'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['sent_date']},
        ),
    ]