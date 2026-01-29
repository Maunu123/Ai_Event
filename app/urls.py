from django.urls import path
from .views import ingest_event
from .views import get_events
from .views import worker_metrics,factory_metrics,workstation_metrics
from .views import Dashboard



urlpatterns = [
    path('events/',get_events),
    path('app/', ingest_event),
    path('metrics/workers/', worker_metrics),
    path('metrics/factory/', factory_metrics), 
    path('metrics/workstations/', workstation_metrics),
    path('Dashboard/',Dashboard,name='Dashboard')
    
]
