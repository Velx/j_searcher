from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.views import View

from searcher.models import TitleInProgress, TypeForList, TitleList, MangaTranslators, AnimeTranslators
from searcher.forms import MalUpdateForm, MangaTranslatorsForm, AnimeTranslatorsForm

import requests as req
import re
import json
from bs4 import BeautifulSoup
# Create your views here.

# def index(request):
#     if request.method == 'GET':
#         return render(request, 'searcher/index.html', )
#     return HttpResponse(status=405)

class Index(View):
    template_name = 'searcher/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            manga = TitleInProgress.objects.filter(
                user__username=request.user,
                title__type__type='MG')
            anime = TitleInProgress.objects.filter(
                user__username=request.user,
                title__type__type='AN')
            return render(request, self.template_name, {'mangas': manga, 'animes':anime})
        else:
            return render(request, self.template_name)

class ChapInc(View):
    def post(self, request, *args, **kwargs):
        title = TitleInProgress.objects.get(pk=request.POST['pk'])
        title.last_chap += 1
        title.save()
        return HttpResponseRedirect('/')

class ChapDec(View):
    def post(self, request, *args, **kwargs):
        title = TitleInProgress.objects.get(pk=request.POST['pk'])
        title.last_chap -= 1
        title.save()
        return HttpResponseRedirect('/')

class UserProfile(View):
    template_name = 'searcher/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.username not in request.get_full_path():
            return HttpResponseForbidden()
        form = MalUpdateForm(initial={'mal_account': request.user.mal_account})
        mform = MangaTranslatorsForm(request.user)
        aform = AnimeTranslatorsForm(request.user)
        count = len(TitleInProgress.objects.filter(user__username=request.user))
        return render(request, self.template_name, {'count':count, 'form':form,
                                                    'mform':mform, 'aform':aform})

class MalUpdate(View):
    def post(self, request, *args, **kwargs):
        request.user.users_titles.clear()
        request.user.mal_account = request.POST["mal_account"]
        request.user.save()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        t_m, c_m = TypeForList.objects.get_or_create(type='MG')
        url = f'https://myanimelist.net/mangalist/{request.POST["mal_account"]}?status=1'
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
                    user=request.user,
                    title=m,
                    last_chap=dict_["num_read_chapters"],
                )
                person_manga.save()
        t_a, c_a = TypeForList.objects.get_or_create(type='AN')
        url = f'https://myanimelist.net/animelist/{request.POST["mal_account"]}?status=1'
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
                    user=request.user,
                    title=a,
                    last_chap=dict_["num_watched_episodes"],
                )
                person_anime.save()
        return HttpResponseRedirect('user/' + request.user.username)


class MangaTranslatorsSet(View):
    def post(self, request, *args, **kwargs):
        form = MangaTranslatorsForm(request.user, request.POST)
        if form.is_valid():
            request.user.manga_translator = MangaTranslators.objects.get(pk=request.POST['manga_translator'])
            request.user.save()
        return HttpResponseRedirect('user/' + request.user.username)


class AnimeTranslatorsSet(View):
    def post(self, request, *args, **kwargs):
        form = AnimeTranslatorsForm(request.user, request.POST)
        if form.is_valid():
            request.user.anime_translator = AnimeTranslators.objects.get(pk=request.POST['anime_translator'])
            request.user.save()
        return HttpResponseRedirect('user/' + request.user.username)