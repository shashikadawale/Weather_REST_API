from django.urls import path, include
from . import views
from django.conf.urls import url
from rest_framework import routers

router = routers.DefaultRouter()
# url/api/locations
router.register('locations', views.LocationView)
# url/api/metrics
router.register('metrics', views.MetricView)
# url/api/data
router.register('data', views.DataView)

view = views.WeatherDataList.as_view({'get': 'list', 'queryset': 'data'})

urlpatterns = [
	path('', include(router.urls)),

    # url/api/search/?location=lname&metric=mname&sdate=YYYY-MM&edate=YYYY-MM
	url('search/(?P<parameters>.*)', view),
]
