# Generated by Django 3.0.5 on 2021-10-27 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0008_auto_20211027_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='igphoto',
            name='visit',
            field=models.IntegerField(default=0),
        ),
    ]
