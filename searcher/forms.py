from django.forms import ValidationError

from django.contrib.auth.forms import UserCreationForm

from searcher.models import CustomUser

import requests as req

class CustomCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'mal_account')

    def __init__(self, *args, **kwargs):
        super(CustomCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def clean_mal_account(self):
        data = self.cleaned_data['mal_account']
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        _url = f'https://myanimelist.net/mangalist/{data}'
        http = req.get(_url, _headers)
        if http.status_code == 404:
            raise ValidationError('This profile does not exist')
        http.close()
        return data
