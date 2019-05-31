# Generated by Django 2.1.4 on 2019-03-16 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warhammer', '0010_step1model_step2model'),
    ]

    operations = [
        migrations.CreateModel(
            name='DwarfStartingProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_range', models.CharField(max_length=10)),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warhammer.ProfessionModel')),
            ],
        ),
        migrations.CreateModel(
            name='ElfStartingProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_range', models.CharField(max_length=10)),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warhammer.ProfessionModel')),
            ],
        ),
        migrations.CreateModel(
            name='HalflingStartingProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_range', models.CharField(max_length=10)),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warhammer.ProfessionModel')),
            ],
        ),
        migrations.CreateModel(
            name='HumanStartingProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_range', models.CharField(max_length=10)),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warhammer.ProfessionModel')),
            ],
        ),
    ]
