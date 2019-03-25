from django import forms
import time
from time import gmtime, strftime
from django.utils import timezone
from datetime import datetime
import requests
from .models import Weather

current_year, current_month, current_day = strftime("%Y", gmtime()), strftime("%m", gmtime()), strftime("%d", gmtime())
next_month = datetime.strptime(('0' + str(int(current_month)+1)), "%m")
next_month_in_B = datetime.strftime(next_month, "%B")
year = {current_year}
if int(current_day) > 26:
    month = {current_month: strftime("%B", gmtime()), next_month:next_month_in_B}
else:
    month = {current_month: strftime("%B", gmtime())}

# all_city = []
# for i in city_dict:
#     all_city.append(i['name_city'])


class SelectDateForm(forms.Form):
    start_date = forms.DateField(initial=timezone.now(), widget=forms.SelectDateWidget(years = year, months = month))
    end_date = forms.DateField(initial=timezone.now(), widget=forms.SelectDateWidget(years = year, months = month))
    my_city = forms.ModelChoiceField(queryset = Weather.objects.values('name_city').distinct())
