# Generated by Django 3.0.5 on 2021-10-26 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0003_userinfo_candidate'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='ig_account',
            field=models.CharField(default='account', max_length=32, verbose_name='ig帳號'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='ig_avatar',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='ig_photo',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='CandidateDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ig_avatar', models.TextField(blank=True, null=True)),
                ('ig_photo', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member.UserInfo')),
            ],
        ),
    ]
