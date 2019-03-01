from django.db import models

class Metric(models.Model):
	metric = models.CharField(max_length=50)

	def __str__(self):
		return self.metric

class Location(models.Model):
	location = models.CharField(max_length=50)

	def __str__(self):
		return self.location

class Data(models.Model):
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	metric = models.ForeignKey(Metric, on_delete=models.CASCADE)
	value = models.FloatField()
	date = models.DateField()

	def __str__(self):
		return f'{self.location}-{self.metric}-{self.date}: {self.value}'
