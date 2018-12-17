from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.views import View

from searcher.models import TitleInProgress, TypeForList, TitleList, MangaTranslators, AnimeTranslators
from searcher.forms import MalUpdateForm, MangaTranslatorsForm, AnimeTranslatorsForm

import requests as req
import re, json, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
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


def mfox_search(title, last_chap, store):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    # TODO: проверка на точное совпадение названий
    # TODO: исправление названий
    url = f'https://fanfox.net/search?title=&genres=&st=1&sort=4&stype=1&name_method=cw&name={title}&author_method=ew&author=&artist_method=cw&artist=&type=&rating_method=eq&rating=&released_method=eq&released='
    http = req.get(url, headers)
    soup = BeautifulSoup(http.text, 'lxml')
    data = soup.find('ul', attrs={'class': 'manga-list-4-list line'})
    if data == None:
        if ":" in title:
            title = title.split(":")[0]
            url = f'https://fanfox.net/search?title=&genres=&st=1&sort=4&stype=1&name_method=cw&name={title}&author_method=ew&author=&artist_method=cw&artist=&type=&rating_method=eq&rating=&released_method=eq&released='
            http = req.get(url, headers)
            soup = BeautifulSoup(http.text, 'lxml')
            data = soup.find('ul', attrs={'class': 'manga-list-4-list line'})
        else:
            title = "".join(title.split())
            url = f'https://fanfox.net/search?title=&genres=&st=1&sort=4&stype=1&name_method=cw&name={title}&author_method=ew&author=&artist_method=cw&artist=&type=&rating_method=eq&rating=&released_method=eq&released='
            http = req.get(url, headers)
            soup = BeautifulSoup(http.text, 'lxml')
            data = soup.find('ul', attrs={'class': 'manga-list-4-list line'})
    name = data.findAll('p', attrs={'class': 'manga-list-4-item-title'})
    l_c = data.findAll('p', attrs={'class': 'manga-list-4-item-tip'})[1::3]
    for i, l in zip(name, l_c):  # TODO: выборка только 1
        cha = re.search(r'Ch\.\d+', l.get_text())
        if last_chap < float(cha.group(0)[3:]):
            store[title] = cha.group(0)[3:]
        else:
            break

def mtail_search(title, last_chap, store):
    # TODO: проверить работоспособность на нормальном аккаунте
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    url = f'https://www.mangatail.me/search/node/{title}'
    http = req.get(url, headers)
    soup = BeautifulSoup(http.text, 'lxml')
    data = soup.find('ol', attrs={'class': 'search-results node-results'})
    if data == None:
        pass
    else:
        data =data.findAll('a')
        for manga in data:
            print(manga.string)
            if manga.string.startswith(title):
                http = req.get(manga['href'], headers)
                soup = BeautifulSoup(http.text, 'lxml')
                _field = soup.find('tbody').find('tr')
                chapter = _field.find('a').string
                lchapter = chapter.split(' ')[-1]
                if last_chap < float(lchapter):
                    store[title] = lchapter
                else:
                    break
            break


def mdex_search(title, last_chap, store):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
        'mangadex_display_lang': 1,
        'mangadex_filter_langs': 1,
        'mangadex_theme': 1
    }
    cookie = {'mangadex_filter_langs': "1"}
    url = f'https://mangadex.org/?page=search&title={title}&genres_exc=7'
    http = req.get(url, headers)
    soup = BeautifulSoup(http.text, 'lxml')
    data = soup.findAll('div', attrs={'class': 'manga-entry col-lg-6 border-bottom pl-0 my-1'})
    if data == None:
        print(title + 'Not found')
    else:
        for item in data:
            manga = item.find('a', attrs={'class': 'ml-1 manga_title text-truncate'})
            if manga.string.startswith(title):
                http = req.get('https://mangadex.org' + manga['href'], headers, cookies=cookie)
                soup = BeautifulSoup(http.text, 'lxml')
                _field = soup.find('div', attrs={'class': 'col col-lg-5 row no-gutters align-items-center flex-nowrap text-truncate pr-1 order-lg-2'})
                if _field == None:
                    pass
                else:
                    _field = _field.find('a').text
                    print(_field)
                    print(title)
                    nchap = re.search(r'(Ch\. \d+.\d)|(Ch\. \d+)', _field).group(0)[4:]
                    print(title + " " + nchap)
                    if last_chap < float(nchap):
                        store[title] = nchap
                    else:
                        break
                break


class MangaUpdates(View):

    template_name = 'searcher/manga_update.html'

    def get(self, request, *args, **kwargs):
        mangas = TitleInProgress.objects.filter(
            user__username=request.user,
            title__type__type='MG')
        store = dict()

        if request.user.manga_translator == MangaTranslators.objects.get(name='Mangafox'):
            for manga in mangas:
                mfox_search(str(manga.title), manga.last_chap, store)
        elif request.user.manga_translator == MangaTranslators.objects.get(name='Mangatail'):
            for manga in mangas:
                mtail_search(str(manga.title), manga.last_chap, store)
        elif request.user.manga_translator == MangaTranslators.objects.get(name='Mangadex'):
            for manga in mangas:
                mdex_search(str(manga.title), manga.last_chap, store)
        else:
            HttpResponseRedirect('/')
        return render(request, self.template_name, {'mangas':store})


def crunch_search(anime_title, w_episodes, v_url, store):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
    }
    url = 'https://myanimelist.net' + v_url
    http = req.get(url, headers)
    soup = BeautifulSoup(http.text, 'lxml')
    if not 'Too Many Requests' in soup.text:
        data = soup.find('div', attrs={'class': 'video-list-outer'}).find('span', attrs={'class': 'title'})
        if float(data.contents[0].split()[1]) > float(w_episodes):
            store[anime_title] = data.contents[0].split()[1]
            time.sleep(0.200)
        else:
            time.sleep(0.200)
    else:
        time.sleep(0.200)
        crunch_search(anime_title, w_episodes, v_url, store)


def hsubs_search(anime_title, w_episodes, store):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
    }
    url = f'https://horriblesubs.info/api.php?method=search&value={anime_title}'
    http = req.get(url, headers)
    soup = BeautifulSoup(http.text, 'lxml')
    data = soup.find('li')
    if data == None:
        if 'nd Season' in anime_title:
            a_t = re.split(r'\dnd Season', anime_title)[0]
            url = f'https://horriblesubs.info/api.php?method=search&value={a_t}'
            http = req.get(url, headers)
            soup = BeautifulSoup(http.text, 'lxml')
            data = soup.find('li')
            _date = data.find('span', attrs={'class': 'latest-releases-date'}).string
            delta = None
            if not _date in ['Today', 'Yesterday']:
                _date = datetime.strptime(_date, '%m/%d/%y').date()
                delta = (datetime.today().date() - _date).days
            if _date == 'Today' or _date =='Yesterday' or delta <= 14:
                data = data.find('strong')
                if float(data.string) > float(w_episodes):
                    store[anime_title] = data.string
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        data = data.find('strong')
        if float(data.string) > float(w_episodes):
            store[anime_title] = data.string
        else:
            pass


class AnimeUpdates(View):

    template_name = 'searcher/anime_update.html'

    def get(self, request, *args, **kwargs):
        animes = TitleInProgress.objects.filter(
            user__username=request.user,
            title__type__type='AN')
        store = dict()
        if request.user.anime_translator == AnimeTranslators.objects.get(name='HorribleSubs'):
            for anime in animes:
                hsubs_search(str(anime.title), anime.last_chap, store)
        elif request.user.anime_translator == AnimeTranslators.objects.get(name='Crunchyroll'):
            for anime in animes:
                crunch_search(str(anime.title), anime.last_chap, str(anime.title.url), store)
        else:
            HttpResponseRedirect('/')
        return render(request, self.template_name, {'animes':store})