from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import View

from searcher.models import TitleInProgress
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