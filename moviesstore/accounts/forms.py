from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django_countries.fields import CountryField

from .models import Profile
class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))
class CustomUserCreationForm(UserCreationForm):
    region = CountryField().formfield()

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2', 'region']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        region = self.cleaned_data.get('region')
        if commit:
            Profile.objects.create(user=user, region=region)
        else:
            self._profile_region = region
        return user
        
        
