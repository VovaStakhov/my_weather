from django.db import models

class Weather(models.Model):
    name_city = models.CharField(max_length = 30)
    temperature = models.FloatField()
    date = models.FloatField()
    objects = models.Manager ()
 
    def _str_(self):
        return self.name_city

class Date(models.Model):
    start_date = models.FloatField()
    end_date = models.FloatField()
    objects = models.Manager ()
