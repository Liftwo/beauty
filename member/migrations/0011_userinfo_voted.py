# Generated by Django 3.0.5 on 2021-10-28 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0010_userinfo_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='voted',
            field=models.BooleanField(default=False),
        ),
    ]
