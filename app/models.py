from django.db import models

class Worker(models.Model):
    worker_id=models.CharField(max_length=10,unique=True)
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Workstation(models.Model):
    station_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Event(models.Model):
    EVENT_TYPES = [
        ('working', 'Working'),
        ('idle', 'Idle'),
        ('absent', 'Absent'),
        ('product_count', 'Product Count'),
    ]

    timestamp = models.DateTimeField()
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    confidence = models.FloatField()
    count = models.IntegerField(default=0)


