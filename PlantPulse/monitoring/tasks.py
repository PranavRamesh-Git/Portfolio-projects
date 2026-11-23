from celery import shared_task
import random
from decimal import Decimal

from celery import shared_task
from django.utils import timezone

from .models import Sensor, Reading
from django.utils import timezone

@shared_task
def test_celery():

    print("CELERY TASK EXECUTED SUCCESSFULLY")

    return "PlantPulse Celery is working"









def generate_pressure_readings():

    if random.random() < 0.05:
        return round(random.uniform(3, 7), 2)

    return round(random.uniform(2, 6), 2)


def generate_temperature_readings():

    if random.random() < 0.05:
        return round(random.uniform(80, 150), 2)

    return round(random.uniform(20, 78), 2)


def generate_vibration_readings():

    return round(random.uniform(7, 20), 2)


@shared_task
def readings():

    sensor_config = {
        15: generate_pressure_readings,
        16: generate_temperature_readings,
        17: generate_vibration_readings,
        29: generate_pressure_readings,
        18: generate_temperature_readings,
        46: generate_temperature_readings
    }

    count = 0

    for sensor_id, generator in sensor_config.items():

        value = generator()

        Reading.objects.create(
            sensor_id=sensor_id,
            value=value,
            recorded_at=timezone.now()
        )

        count += 1

    return f"{count} readings generated"

