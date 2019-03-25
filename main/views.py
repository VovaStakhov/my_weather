from django.shortcuts import render
import requests
from .models import Weather, Date
from django.db import connection
from datetime import datetime
import time
from time import gmtime, strftime
from .forms import SelectDateForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


APPID = 'f378750125cbc86765c91aac9075c0d7'


def index(request):
    city = request.POST.get('city', False)
    url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid={}'

    weather_data = []

    try:
        city_weather = requests.get(url.format(city, APPID)).json()

        if city != False:

            for i in city_weather['list']:

                weather = {
                    'status': 'Your weather:',
                    'city': 'In ' + city,
                    'temperature': i['main']['temp'],
                    'units': '° C now.',
                    'more': 'more info...',
                }
                weather_data.append(weather)

                s = i["dt_txt"]
                d = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                time_seconds = time.mktime(d.timetuple())
                q = Weather(name_city=city,
                            temperature=i['main']['temp'], date=time_seconds)
                q.save()

            context = {'weather_data': weather_data[0]}
            return render(request, 'search.html', context)
        else:
            return render(request, 'search.html')
    except KeyError:
        weather = {
            'status': 'Type your city correctly!',
            'city': '',
            'temperature': '',
            'units': '',
            'more': '',
        }
        weather_data.append(weather)
        context = {'weather_data': weather_data[0]}
        return render(request, 'search.html', context)


def get_data(request):
    start_year, start_month, start_day = request.POST.get('start_date_year', strftime("%Y", gmtime())), request.POST.get(
        'start_date_month', strftime("%m", gmtime())), request.POST.get('start_date_day', strftime("%d", gmtime()))
    start_date = start_year + '/'+start_month + '/'+start_day
    start_date = datetime.strptime(start_date, "%Y/%m/%d")
    start_date = time.mktime(start_date.timetuple())

    end_year, end_month, end_day = request.POST.get('end_date_year', strftime("%Y", gmtime())), request.POST.get(
        'end_date_month', strftime("%m", gmtime())), request.POST.get('end_date_day', strftime("%d", gmtime()))
    end_date = end_year + '/'+end_month + '/' + end_day
    end_date = datetime.strptime(end_date, "%Y/%m/%d")
    end_date = time.mktime(end_date.timetuple())

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM main_weather ORDER BY ID DESC LIMIT 1')
    city = cursor.fetchall()
    city = city[0][1]
    my_city = request.POST.get('my_city', city) 
    

    return ({'start_date': start_date, 'end_date': end_date, 'my_city': my_city}) 

def convert_time(i):
    return {'my_city': i[0], 'my_temp': i[1], 'my_date': datetime.fromtimestamp(i[2]).strftime("%B %d, %H:%M")}

def result(request):

    my_result = []
    select_date = request.POST.get('end_date_day', False)
    select_page = request.GET.get('page', False)

    if (select_date == False) and (select_page == False):
        date_field = SelectDateForm()
        choice_field = SelectDateForm()
        message = 'Choose you city and date'
        context= {'message':message, 'date_field': date_field, 'choice_field': choice_field}
        return render(request, 'result.html', context)
    elif select_date == False:
        date_field = SelectDateForm()
        choice_field = SelectDateForm()
        cursor = connection.cursor()
        cursor.execute('SELECT start_date FROM main_date ORDER BY ID DESC LIMIT 1')
        start_date = cursor.fetchall()[0][0]
        cursor.execute('SELECT end_date FROM main_date ORDER BY ID DESC LIMIT 1')
        end_date = cursor.fetchall()[0][0]
        cursor.execute('SELECT my_city FROM main_date ORDER BY ID DESC LIMIT 1')
        my_city = cursor.fetchall()[0][0]
        cursor.execute('SELECT DISTINCT name_city, temperature, date FROM main_weather WHERE name_city = %s AND date BETWEEN %s AND %s GROUP BY date', [my_city, start_date, end_date])
        my_result = cursor.fetchall()
        my_data = list(map(convert_time, my_result))
        paginator = Paginator(my_data, 8)
        page = request.GET.get('page')  
        my_data = paginator.get_page(page)
        message = str('Weather in ' + str(my_city) + ' from ' + str(datetime.fromtimestamp(start_date).strftime("%d %B")) + ' to ' + str(datetime.fromtimestamp(end_date).strftime("%d %B")) + ':')
        context= {'message': message, 'my_data': my_data, 'my_city': my_city, 'date_field': date_field, 'choice_field': choice_field}
        return render(request, 'result.html', context)
    else:
        if request.method == 'POST':
            date_field = SelectDateForm(request.POST)
            choice_field = SelectDateForm(request.POST)
        date_field = SelectDateForm()
        choice_field = SelectDateForm()

        period = get_data(request)
        start_date = period['start_date']
        end_date = period['end_date'] + 86399
        my_city = period['my_city']

        if start_date <= end_date:
            q = Date(start_date=start_date, end_date=end_date, my_city=my_city)
            q.save()
            cursor = connection.cursor()
            cursor.execute('SELECT DISTINCT name_city, temperature, date FROM main_weather WHERE name_city = %s AND date BETWEEN %s AND %s GROUP BY date', [my_city, start_date, end_date])
            my_result = cursor.fetchall()
            my_data = list(map(convert_time, my_result))
            paginator = Paginator(my_data, 8)
            my_data = paginator.get_page(1)
            message = str('Weather in ' + str(my_city) + ' from ' + str(datetime.fromtimestamp(start_date).strftime("%d %B")) + ' to ' + str(datetime.fromtimestamp(end_date).strftime("%d %B")) + ':')
            context= {'message': message, 'my_data': my_data, 'my_city': my_city, 'date_field': date_field, 'choice_field': choice_field}
            return render(request, 'result.html', context)
        else:
            message= 'Choose correct date range!'
            context = {'date_field': date_field, 'choice_field': choice_field, 'message': message}
            return render(request, 'result.html', context)
