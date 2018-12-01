from django.contrib.auth.forms import UserCreationForm

from searcher.models import CustomUser


class CustomCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'mal_account')