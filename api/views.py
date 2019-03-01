from datetime import datetime, date
from rest_framework import viewsets
from .models import Location, Metric, Data
from rest_framework.response import Response
from .serializers import LocationSerializer, MetricSerializer, DataSerializer

class LocationView(viewsets.ModelViewSet):
    '''
    This class gets the data from Location model and
    serializes it. Works as a view for locations.
    output: serialized data for Location model
    '''
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class MetricView(viewsets.ModelViewSet):
    '''
    This class gets the data from Metric model and
    serializes it. Works as a view for metrics.
    output: serialized data for Metric model
    '''
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer

class DataView(viewsets.ModelViewSet):
    '''
    This class gets the data from Data model and
    serializes it. Works as a view for weather data.
    output: serialized data for Data model
    '''
    queryset = Data.objects.all()
    serializer_class = DataSerializer


class WeatherDataList(viewsets.GenericViewSet):
    '''
    This class provides a interface for querying data via url.
    This class also converts data to customize format.
    '''
    serializer_class = DataSerializer
    data = Data.objects.all()

    def list(self, request, *args, **kwargs):
        '''
        Get parameters through url.
        Example:-
            url/api/search/?location=lname&metric=mname&sdate=YYYY-MM&edate=YYYY-MM
        This method parse the data and convert it to customized format.
        input: fetches parameters from url
        output: returns customized response based on parameters
        '''
        location = self.request.query_params.get('location', None).capitalize()
        metric = self.request.query_params.get('metric', None).capitalize()
        sdate = self.request.query_params.get('sdate', None)
        edate = self.request.query_params.get('edate', None)

        # add -1(day) to date format as the data stored in model is formatted as YYYY-MM-DD
        sdate += '-1'
        edate += '-1'
        
        # convert date_string to date format
        temp_sdate = list(map(int, sdate.split('-')))
        temp_edate = list(map(int, edate.split('-')))
        sdate = date(*temp_sdate)
        edate = date(*temp_edate)

        # filter data with respect to parameters passed
        filtered_data = Data.objects.filter(date__range=(sdate, edate),
                                            location__location=location,
                                            metric__metric=metric)

        # create customized response
        # return data as [{'YYYY-MM': value}, ...]
        custom_response = [
        	{f'{date.year}-{date.month}' : value}
        	for (date, value) in
        	filtered_data.values_list('date', 'value').order_by('date')
        ]

        # print(len(custom_response))
        return Response(custom_response)
