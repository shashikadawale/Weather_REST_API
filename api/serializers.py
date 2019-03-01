from rest_framework import serializers
from .models import Location, Metric, Data

class LocationSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Location
		fields = ('location',)

class MetricSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Metric
		fields = ('metric',)

class DataSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Data
		fields = ('location', 'metric', 'value', 'date')
