# Generated by Django 2.1.5 on 2019-02-12 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataApp', '0009_userprofile_favorite_mlb_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasketballTeam',
            fields=[
                ('team_id', models.CharField(max_length=50)),
                ('team_name', models.CharField(max_length=50, primary_key=True, serialize=False)),
            ],
        ),
    ]
