from django.shortcuts import render
from django.http import HttpResponse, Http404

# Create your views here.

def index(request):
    if request.method == 'GET':
        return render(request, 'searcher/index.html', )
    return HttpResponse(status=405)