# Generated by Django 2.2.2 on 2019-06-18 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conditionals', '0002_auto_20190614_2307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conditionalstatement',
            name='action',
        ),
        migrations.RemoveField(
            model_name='conditionalstatement',
            name='reset',
        ),
        migrations.AddField(
            model_name='conditionalstatement',
            name='actions_json_list',
            field=models.CharField(default='[]', max_length=2000),
        ),
        migrations.DeleteModel(
            name='Action',
        ),
    ]
