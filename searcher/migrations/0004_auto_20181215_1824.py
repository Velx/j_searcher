# Generated by Django 2.1.3 on 2018-12-15 15:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0003_titlelist_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='anime_translator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='searcher.AnimeTranslators'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='manga_translator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='searcher.MangaTranslators'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='users_titles',
            field=models.ManyToManyField(null=True, related_name='users', through='searcher.TitleInProgress', to='searcher.TitleList'),
        ),
        migrations.AlterField(
            model_name='titleinprogress',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='searcher.TitleList'),
        ),
        migrations.AlterField(
            model_name='titleinprogress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
