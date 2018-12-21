from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.contrib.auth.models import  AbstractUser

import requests as req
import re
import json
from bs4 import BeautifulSoup


class TypeForList(models.Model):
    manga = ('MG', 'Manga')
    anime = ('AN', 'Anime')
    __all = dict([manga, anime])

    type = models.CharField(max_length=2, choices=__all.items())

    def __str__(self):
        return str(self.__all[self.type])


class TitleList(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey('TypeForList', related_name='types', on_delete=models.PROTECT)
    url = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.name)


class MangaTranslators(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return str(self.name)


class AnimeTranslators(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return str(self.name)


class CustomUser(AbstractUser):
    mal_account = models.CharField(max_length=40)
    users_titles = models.ManyToManyField('TitleList', blank=True, related_name='users',
                                          through='TitleInProgress')
    manga_translator = models.ForeignKey('MangaTranslators', null=True, related_name='users', on_delete=models.SET_NULL)
    anime_translator = models.ForeignKey('AnimeTranslators', null=True, related_name='users', on_delete=models.SET_NULL)



class TitleInProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.ForeignKey(TitleList, on_delete=models.CASCADE)
    last_chap = models.IntegerField()


@receiver(signals.post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
                }
        t_m, c_m = TypeForList.objects.get_or_create(type='MG')
        url = f'https://myanimelist.net/mangalist/{instance.mal_account}?status=1'
        zap = req.get(url, headers)
        soup = BeautifulSoup(zap.text, 'lxml')
        dat = soup.find('table', attrs={'class': 'list-table'})
        if not dat or dat['data-items'] == '[]':
            pass
        else:
            pattern = re.compile("(\{.+?\})")
            field_ = re.findall(pattern, dat['data-items'][1:-1])
            for item in field_:
                dict_ = json.loads(item)
                if dict_["manga_publishing_status"] == 2 or dict_["num_read_chapters"] == 0:
                    continue
                m, creat = TitleList.objects.get_or_create(name=dict_["manga_title"], type=t_m)
                person_manga = TitleInProgress.objects.create(
                    user=instance,
                    title=m,
                    last_chap=dict_["num_read_chapters"],
                )
                person_manga.save()
        t_a, c_a = TypeForList.objects.get_or_create(type='AN')
        url = f'https://myanimelist.net/animelist/{instance.mal_account}?status=1'
        zap = req.get(url, headers)
        soup = BeautifulSoup(zap.text, 'lxml')
        data = soup.find('table', attrs={'class': 'list-table'})
        if not dat or len(data['data-items']) == 2:
            pass
        else:
            pattern = re.compile("(\{.+?\})")
            field_ = re.findall(pattern, data['data-items'][1:-1])
            for item in field_:
                dict_ = json.loads(item)
                if dict_["anime_airing_status"] != 1:
                    continue
                a, creat = TitleList.objects.get_or_create(
                    name=dict_["anime_title"],
                    type=t_a,
                    url=dict_['video_url']
                )
                person_anime = TitleInProgress.objects.create(
                    user=instance,
                    title=a,
                    last_chap=dict_["num_watched_episodes"],
                )
                person_anime.save()
        print('AYAYA. Created')

# @receiver(signals.post_init, sender=CustomUser)
# def manga_init(sender, instance, **kwargs):
#     t, created = TypeForList.objects.get_or_create(type='MG')
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
#     }
#     url = f'https://myanimelist.net/mangalist/{instance.mal_account}?status=1'
#     print(url)
#     zap = req.get(url, headers)
#     soup = BeautifulSoup(zap.text, 'lxml')
#     dat = soup.find('table', attrs={'class': 'list-table'})
#     if not dat or dat['data-items'] == '[]':
#         pass
#     else:
#         pattern = re.compile("(\{.+?\})")
#         field_ = re.findall(pattern, dat['data-items'][1:-1])
#         for item in field_:
#             dict_ = json.loads(item)
#             if dict_["manga_publishing_status"] == 2 or dict_["num_read_chapters"] == 0:
#                 continue
#             m, creat = TitleList.objects.get_or_create(name=dict_["manga_title"], type=t)
#             person_manga = TitleInProgress.objects.create(
#                 user=instance,
#                 title=m,
#                 last_chap=dict_["num_read_chapters"],
#             )
#             person_manga.save()

#
#
# @receiver(signals.post_init, sender=CustomUser)
# def anime_init(sender, instance, **kwargs):
#     t, created = TypeForList.objects.get_or_create(type='AN')
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
#     }
#     url = f'https://myanimelist.net/animelist/{instance.mal_account}?status=1'
#     zap = req.get(url, headers)
#     soup = BeautifulSoup(zap.text, 'lxml')
#     data = soup.find('table', attrs={'class': 'list-table'})
#     try:
#         pattern = re.compile("(\{.+?\})")
#         field_ = re.findall(pattern, data['data-items'][1:-1])
#         if len(data['data-items']) == 2:
#             pass
#         else:
#             for item in field_:
#                 dict_ = json.loads(item)
#                 if dict_["anime_airing_status"] != 1:
#                     continue
#                 a, creat = TitleList.objects.get_or_create(name=dict_["anime_title"], type=t)
#                 person_anime = TitleInProgress.objects.create(
#                     user=instance,
#                     title=a,
#                     last_chap=dict_["num_watched_episodes"],
#                     url=dict_['video_url']
#                 )
#                 person_anime.save()
#     except:
#         pass