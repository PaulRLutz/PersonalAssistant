# Generated by Django 2.2.2 on 2019-06-18 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conditionals', '0003_auto_20190618_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conditionalstatement',
            name='logical_operators',
            field=models.CharField(default='[]', max_length=2000),
        ),
    ]
