# Generated by Django 2.1.3 on 2018-12-08 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0002_auto_20181205_2249'),
    ]

    operations = [
        migrations.AddField(
            model_name='titlelist',
            name='url',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]