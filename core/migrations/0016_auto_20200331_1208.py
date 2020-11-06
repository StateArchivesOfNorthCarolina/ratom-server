# Generated by Django 2.2.10 on 2020-03-31 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20200323_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='import_status',
            field=models.CharField(choices=[('CR', 'Created'), ('IM', 'Importing'), ('CM', 'Complete'), ('RE', 'Restoring'), ('FA', 'Failed')], default='CR', max_length=2),
        ),
    ]