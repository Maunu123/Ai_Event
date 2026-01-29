from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Worker, Workstation, Event
from django.utils.dateparse import parse_datetime

@csrf_exempt
def ingest_event(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)

        WorkerPayload = Worker.objects.get(worker_id=data['worker_id'])
        WorkstationPayload = Workstation.objects.get(station_id=data['workstation_id'])
        print("Worker", WorkerPayload)
        Event.objects.create(
            timestamp=parse_datetime(data['timestamp']),
            worker=WorkerPayload,
            workstation=WorkstationPayload,
            event_type=data['event_type'],
            confidence=data.get('confidence', 0),
            count=data.get('count', 0)
        )

        return JsonResponse({'status': 'success'})

    except Exception as e:
        print(e)
        print("Error")
        return JsonResponse({'error': str(e)}, status=400)
    

def get_events(request):
    events = Event.objects.all().values()
    return JsonResponse(list(events), safe=False)

    

def worker_metrics(request):
    result = []
    workers = Worker.objects.all()

    for worker in workers:
        events = list(Event.objects.filter(worker=worker).order_by('timestamp'))

        working_time = idle_time = 0.0
        total_units = 0

        if not events:
            result.append({
                "worker_id": worker.worker_id,
                "name": worker.name,
                "working_minutes": 0,
                "idle_minutes": 0,
                "utilization_percent": 0,
                "units_produced": 0,
                "units_per_hour": 0
            })
            continue

        # Sum product_count
        for ev in events:
            if ev.event_type == 'product_count' and ev.count:
                total_units += ev.count

        # Compute durations between consecutive events
        for i in range(len(events) - 1):
            current = events[i]
            nxt = events[i + 1]
            duration_min = (nxt.timestamp - current.timestamp).total_seconds() / 60.0

            if current.event_type == 'working':
                working_time += duration_min
            elif current.event_type == 'idle':
                idle_time += duration_min

        # Handle single event or last event: assume 5 min default
        if len(events) == 1 or events[-1].event_type in ['working', 'idle']:
            if events[-1].event_type == 'working':
                working_time += 5
            elif events[-1].event_type == 'idle':
                idle_time += 5

        total_time = working_time + idle_time
        utilization = (working_time / total_time * 100) if total_time > 0 else 0

        # Units per hour
        hours = total_time / 60 if total_time > 0 else 1  # prevent division by zero
        units_per_hour = round(total_units / hours, 2)

        result.append({
            "worker_id": worker.worker_id,
            "name": worker.name,
            "working_minutes": round(working_time, 2),
            "idle_minutes": round(idle_time, 2),
            "utilization_percent": round(utilization, 2),
            "units_produced": total_units,
            "units_per_hour": units_per_hour
        })

    return JsonResponse(result, safe=False)


def workstation_metrics(request):
    result = []
    stations = Workstation.objects.all()

    for station in stations:
        events = list(Event.objects.filter(workstation=station).order_by('timestamp'))

        occupancy = 0.0
        total_units = 0

        if not events:
            result.append({
                "station_id": station.station_id,
                "name": station.name,
                "occupancy_minutes": 0,
                "utilization_percent": 0,
                "units_produced": 0,
                "throughput_per_hour": 0
            })
            continue

        # Sum product_count
        for ev in events:
            if ev.event_type == 'product_count' and ev.count:
                total_units += ev.count

        # Compute durations
        for i in range(len(events) - 1):
            current = events[i]
            nxt = events[i + 1]
            duration_min = (nxt.timestamp - current.timestamp).total_seconds() / 60.0
            if current.event_type == 'working':
                occupancy += duration_min

        # Handle last event
        if events[-1].event_type == 'working':
            occupancy += 5

        # Observation window: first → last
        obs_minutes = (events[-1].timestamp - events[0].timestamp).total_seconds() / 60.0
        obs_minutes = obs_minutes if obs_minutes > 0 else occupancy  # prevent division by zero

        utilization_percent = round((occupancy / obs_minutes) * 100, 2) if obs_minutes > 0 else 0

        # Throughput per hour
        hours = obs_minutes / 60
        throughput_per_hour = round(total_units / hours, 2) if hours > 0 else total_units

        result.append({
            "station_id": station.station_id,
            "name": station.name,
            "occupancy_minutes": round(occupancy, 2),
            "utilization_percent": utilization_percent,
            "units_produced": total_units,
            "throughput_per_hour": throughput_per_hour
        })

    return JsonResponse(result, safe=False)


def factory_metrics(request):
    workers = Worker.objects.all()

    total_working = total_idle = 0.0
    total_units = 0
    utilization_sum = 0.0
    active_workers = 0

    for worker in workers:
        events = list(Event.objects.filter(worker=worker).order_by('timestamp'))

        working_time = idle_time = 0.0

        if not events:
            continue

        # sum product_count
        for ev in events:
            if ev.event_type == 'product_count' and ev.count:
                total_units += ev.count

        # compute durations
        for i in range(len(events) - 1):
            current = events[i]
            nxt = events[i + 1]
            duration_min = (nxt.timestamp - current.timestamp).total_seconds() / 60.0

            if current.event_type == 'working':
                working_time += duration_min
            elif current.event_type == 'idle':
                idle_time += duration_min

        # last event default 5 min
        if events[-1].event_type == 'working':
            working_time += 5
        elif events[-1].event_type == 'idle':
            idle_time += 5

        if working_time + idle_time > 0:
            utilization_sum += (working_time / (working_time + idle_time)) * 100
            active_workers += 1

        total_working += working_time
        total_idle += idle_time

    avg_utilization = (utilization_sum / active_workers) if active_workers > 0 else 0

    return JsonResponse({
        "total_productive_minutes": round(total_working, 2),
        "total_idle_minutes": round(total_idle, 2),
        "total_units_produced": total_units,
        "average_utilization_percent": round(avg_utilization, 2)
    })


def Dashboard(request):
    """
    Render the Dashboard template.
    Actual data will be fetched via AJAX from APIs.
    """
    return render(request, 'Dashboard.html')


