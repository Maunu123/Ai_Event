# AI-Powered Worker Productivity Dashboard

## Project Overview

This is a full-stack web application for monitoring and analyzing worker productivity in a factory using AI-generated CCTV events. The system ingests structured events, stores them in a database, computes productivity metrics, and displays them in a dashboard.

---

## Features

- **Worker-level metrics**
  - Total active (working) minutes
  - Total idle minutes
  - Utilization percentage
  - Total units produced
  - Units per hour

- **Workstation-level metrics**
  - Occupancy minutes
  - Utilization percentage
  - Total units produced
  - Throughput per hour

- **Factory-level metrics**
  - Total productive minutes
  - Total idle minutes
  - Total units produced
  - Average utilization across workers

- **Dashboard**
  - Factory summary
  - Worker metrics table
  - Workstation metrics table

- **Backend API**
  - `/api/app/` → POST AI-generated events
  - `/api/metrics/workers/` → GET worker metrics
  - `/api/metrics/workstations/` → GET workstation metrics
  - `/api/metrics/factory/` → GET factory summary metrics

- **Database**
  - Stores workers, workstations, and AI events (SQLite by default)
  - Metrics are computed dynamically from stored events

---

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd AiEvent
````

2. **Create a virtual environment and activate**

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser (optional)**

```bash
python manage.py createsuperuser
```

6. **Run the server**

```bash
python manage.py runserver
```

7. **Access**

* API: `http://127.0.0.1:8000/api/`
* Dashboard: `http://127.0.0.1:8000/dashboard/`

---

## Database Schema

**Workers**

* `worker_id` (str)
* `name` (str)

**Workstations**

* `station_id` (str)
* `name` (str)

**Events**

* `timestamp` (datetime)
* `worker` (FK → Worker)
* `workstation` (FK → Workstation)
* `event_type` (working, idle, absent, product_count)
* `confidence` (float)
* `count` (int, units produced if `product_count`)

---

## Metric Calculations

**Worker-level**

* `working_minutes` = sum of durations between consecutive 'working' events
* `idle_minutes` = sum of durations between consecutive 'idle' events
* `utilization_percent` = `working_minutes / (working_minutes + idle_minutes) * 100`
* `units_produced` = sum of `count` from 'product_count' events
* `units_per_hour` = `units_produced / (total_time / 60)`

**Workstation-level**

* `occupancy_minutes` = sum of durations where worker was 'working' at that station
* `utilization_percent` = `occupancy_minutes / observation_window * 100`
* `throughput_per_hour` = `units_produced / (observation_window / 60)`

**Factory-level**

* `total_productive_minutes` = sum of all worker `working_minutes`
* `total_idle_minutes` = sum of all worker `idle_minutes`
* `total_units_produced` = sum of all `units_produced`
* `average_utilization_percent` = average utilization of active workers

---

## Assumptions & Trade-offs

* Time between events is measured in minutes.
* Last event duration defaults to 5 minutes if no subsequent event.
* Out-of-order timestamps are ignored; events are sorted before computation.
* Duplicate events are counted as separate occurrences.
* Designed for 6 workers and 6 workstations (can scale with more).


## Theoretical Questions

**1. Handling intermittent connectivity:**
Store events locally and sync with the backend when connection is restored.

**2. Detecting duplicate events:**
Check for identical timestamp + worker + workstation + event_type before insertion.

**3. Out-of-order timestamps:**
Sort events by timestamp before metric calculation.

**4. Scaling to multiple cameras/sites:**

* Use separate event queues per camera/site.
* Aggregate metrics in a central database or data warehouse.
* Use background tasks (Celery/RQ) for processing large-scale events.





## Technologies Used

* Python 3.13
* Django 4.x
* SQLite
* HTML / JS / CSS for dashboard
* Requests library for sending events
