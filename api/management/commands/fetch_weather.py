from django.core.management.base import BaseCommand
import requests as req
from api.models import Location, Metric, Data
from itertools import product
from datetime import datetime
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Getting data based on locations and metrics'

    def handle(self, *args, **kwargs):
        locations = ('UK', 'England', 'Wales', 'Scotland')
        metrics = ('Tmin', 'Tmax', 'Rainfall')
        # combinations of locations and metrics
        loc_x_met = list(product(locations, metrics))
        for loc, met in loc_x_met:
            # fetch data from url
            url = f'https://s3.eu-west-2.amazonaws.com/interview-question-data/metoffice/{met}-{loc}.json'
            response = req.get(url)
            data = response.json()
            status = self.check_existence(data, met, loc)
            if status:
                print(f'Already exists data for values {met}-{loc}')
            else:
                Data.objects.filter(location__location=loc, metric__metric=met).delete()
                print(f'Adding data for {met}-{loc}')
                self.orm_bulk_create(data, met, loc)
        print('Data successfully added to models/database.')

    def check_existence(self, data, met, loc):
        '''
        check_existence method checks size of data if equal to previous data put
        into database/model based on location and metric.
        input: json_data, metric, location
        output: returns boolean
        '''
        size_existed_data = Data.objects.filter(location__location=loc, metric__metric=met).count()
        return size_existed_data == len(data)

    def orm_bulk_create(self, data, metric, location):
        '''
        orm_bulk_create method adds data to database/model using bulk_create()
        method.
        input: json_data, metric, location
        Result: data added to the database
        '''
        try:
            if not Location.objects.filter(location=location):
                l = Location.objects.create(location=location)
            if not Metric.objects.filter(metric=metric):
                m = Metric.objects.create(metric=metric)
            l = Location.objects.filter(location=location)[0]
            m = Metric.objects.filter(metric=metric)[0]

            # create a list of entries that will be added to database
            instances = [
                Data(
                location=l,
                metric=m,
                value=data[i]['value'],
                date = '{0}-{1:02}-1'.format(datetime.strptime(str(data[i]['year'])
                                        + "-" +str(data[i]['month']), '%Y-%m').year,
                                        datetime.strptime(str(data[i]['year'])
                                        + "-" + str(data[i]['month']), '%Y-%m').month)
                )
                for i in range(len(data))
            ]
            Data.objects.bulk_create(instances)
        except OperationalError as op_error:
            print('Databse connection problem : ', op_error)
        except Exception as exp:
            print('Error occured', exp)
