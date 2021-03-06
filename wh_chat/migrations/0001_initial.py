# Generated by Django 3.0.5 on 2020-05-15 12:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NPCModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('WW', models.IntegerField()),
                ('US', models.IntegerField()),
                ('notes', models.TextField(max_length=1000)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wh_chat.GameModel')),
            ],
        ),
        migrations.CreateModel(
            name='MessagesModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.TextField(max_length=100)),
                ('message', models.TextField(max_length=1000)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wh_chat.GameModel')),
            ],
        ),
        migrations.CreateModel(
            name='MapModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('map', models.TextField(max_length=1000)),
                ('counter', models.IntegerField(default=1)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='wh_chat.GameModel')),
            ],
        ),
    ]
