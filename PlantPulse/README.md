# PlantPulse — Industrial Equipment Monitoring & Automated Sensor Alerts

PlantPulse is a full-stack industrial equipment monitoring application built using **Python, Django, Django REST Framework, PostgreSQL, Redis, Celery, JavaScript, HTML, and CSS**. It enables maintenance teams to monitor factory equipment, track sensor readings, detect threshold breaches, and manage equipment alerts, with an emphasis on backend development, database automation, asynchronous task scheduling, and REST API integration.

## Key Features

**Equipment & Sensor Monitoring**

- Facility-based dashboard displaying machine details, operational status, maintenance schedules, and sensor statistics.
- Monitor temperature, vibration, and pressure sensors with configurable minimum and maximum thresholds.
- View sensor readings with timestamps, threshold information, and visual indicators for abnormal readings.
- Update machine maintenance dates and remarks through validated Django ModelForms.

**Automated Alerts & Maintenance Workflows**

- Automatically detect threshold breaches and generate alerts using PostgreSQL triggers.
- Track recurring breaches through occurrence counts and severity escalation.
- Manage alert transitions through Open, Acknowledged, and Resolved statuses.
- Record employee acknowledgement details, resolution notes, and timestamps.
- Generate simulated sensor readings periodically using Celery Beat, Celery workers, and Redis.

**QuickCheck — Sensor Reading API**

- Search sensor readings using unique sensor codes.
- Filter readings by breach status through Django REST Framework query parameters.
- Retrieve paginated sensor data through authenticated REST API endpoints.
- Display API responses dynamically using JavaScript Fetch API.

## Tech Stack

- **Backend:** Python, Django, Django REST Framework, Django ORM
- **Database:** PostgreSQL, SQL, database views, triggers, constraints, indexes, Django migrations
- **Frontend:** HTML, CSS, JavaScript, Django Templates
- **Background Processing:** Celery, Celery Beat, Redis
- **API Development:** DRF ModelSerializer, ListAPIView, filtering, pagination
- **Security:** Django session authentication, password hashing, CSRF protection, login-required views, form validation
- **Testing:** Django TestCase, SimpleTestCase, Django test client

## Technical Highlights

PlantPulse uses Django's Model-View-Template architecture and PostgreSQL relational models to manage facilities, machines, sensors, readings, and alerts. Django ORM queries, database constraints, and indexes support structured data retrieval, threshold validation, and maintenance workflows.

PostgreSQL triggers automatically generate and update sensor alerts when readings exceed configured thresholds, while occurrence counts support severity escalation. Redis-backed Celery workers and Celery Beat periodically generate simulated sensor readings, separating scheduled data generation from HTTP request processing.

Django REST Framework powers QuickCheck, providing authenticated, paginated sensor-reading endpoints with sensor-code and breach-status filtering. JavaScript Fetch API integrates these endpoints into the frontend, while Django ModelForms and class-based views handle equipment updates and alert transitions.

Built to demonstrate practical Python backend engineering, Django application development, relational database design, SQL automation, asynchronous task processing, REST API development, authentication, and automated testing.
