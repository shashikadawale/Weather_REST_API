from django.test import TestCase
from django.db import connections
from django.db.utils import OperationalError
from itertools import product
import requests as req
from random import randint
from api.models import Data
from datetime import date
from django.core.management import call_command
from api.management.commands.fetch_weather import Command

class WeatherDataTest(TestCase):
    '''
    Test module for weather rest api
    '''
    def setUp(self):
        self.db_connect = connections['default']
        self.locations = ('UK', 'England', 'Wales', 'Scotland')
        self.metrics = ('Tmin', 'Tmax', 'Rainfall')
        self.loc_x_met = list(product(self.locations, self.metrics))
        try:
            c = self.db_connect.cursor()
        except OperationalError:
            connected = False
        else:
            connected = True
        self.assertEqual(connected, True)

    def test_filter_weather_data_check(self):
        # fill database with details
        call_command('fetch_weather')
        for loc, met in self.loc_x_met:
            url = f'https://s3.eu-west-2.amazonaws.com/interview-question-data/metoffice/{met}-{loc}.json'
            response = req.get(url)
            data = response.json()
            # passing boundary conditions (first data, last data)
            len_filtered_data = self._get_len_data(data, 0, -1, loc, met)
            self.assertEqual(len_filtered_data, len(data))

            start_index = randint(1, len(data))
            end_index = randint(start_index+1, len(data)+1)
            # passing randomly generated start date and end date (index)
            len_filtered_data = self._get_len_data(data, start_index, end_index, loc, met)
            self.assertEqual(len_filtered_data, len(data[start_index:end_index+1]))

    def _get_len_data(self, data, start_index, end_index, loc, met):
        start_year = data[start_index]['year']
        start_month = data[start_index]['month']
        start_date = date(start_year, start_month, 1)
        end_year = data[end_index]['year']
        end_month = data[end_index]['month']
        end_date = date(end_year, end_month, 1)
        # filter based on passed parameters
        filtered_data = Data.objects.filter(date__range=(start_date, end_date),
                                        location__location=loc,
                                        metric__metric=met)
        return filtered_data.count()

    def test_add_data_db(self):
        len_data = 0
        obj_command = Command()
        for loc, met in self.loc_x_met:
            url = f'https://s3.eu-west-2.amazonaws.com/interview-question-data/metoffice/{met}-{loc}.json'
            response = req.get(url)
            data = response.json()
            status = obj_command.check_existence(data, met, loc)
            if status:
                pass
            else:
                Data.objects.filter(location__location=loc, metric__metric=met).delete()
                obj_command.orm_bulk_create(data, met, loc)
                len_data += len(data)
        self.assertEqual(Data.objects.all().count(), len_data)

    def tearDown(self):
        self.db_connect.close()
