from django.contrib import admin
from .models import Worker,Workstation,Event
admin.site.register(Worker)
admin.site.register(Workstation)
admin.site.register(Event)