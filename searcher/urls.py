from django.urls import path
from django.contrib.auth.views import logout_then_login, LoginView
from django.views.generic import CreateView
from searcher.forms import CustomCreationForm
from searcher.views import ChapInc, ChapDec, UserProfile, MalUpdate, MangaTranslatorsSet, AnimeTranslatorsSet, MangaUpdates, AnimeUpdates

app_name = 'searcher'

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='auth/login.html'
    ), name='login'),

    path('logout/', logout_then_login, name='logout'),

    path('register/', CreateView.as_view(
        template_name='auth/register.html',
        form_class=CustomCreationForm,
        success_url='/',
    ), name='register'),

    path('title/inc', ChapInc.as_view(), name='chap_inc'),
    path('title/dec', ChapDec.as_view(), name='chap_dec'),

    path('user/<str:username>', UserProfile.as_view(), name='profile'),
    path('update_mal', MalUpdate.as_view(), name='update_mal' ),

    path('mtrans_set', MangaTranslatorsSet.as_view(), name='manga_translator_set' ),
    path('atrans_set', AnimeTranslatorsSet.as_view(), name='anime_translator_set' ),
    path('manga_updates', MangaUpdates.as_view(), name='manga_updates'),
    path('anime_updates', AnimeUpdates.as_view(), name='anime_updates'),
]
