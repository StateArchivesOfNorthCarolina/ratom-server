# Generated by Django 2.2.10 on 2020-02-12 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200206_0844'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalmessageaudit',
            old_name='restrictions',
            new_name='restriction',
        ),
        migrations.RenameField(
            model_name='messageaudit',
            old_name='restrictions',
            new_name='restriction',
        ),
    ]