
from django.db import models
from django.db.models import Q, F
from django.utils import timezone

# 1. FACILITY


class Facility(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    country = models.CharField(max_length=80, default="India")
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)    
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name



# 2. MACHINE


class Machine(models.Model):

    MACHINE_TYPES = [
        ("MOTOR", "Motor"),
        ("PUMP", "Pump"),
        ("COMPRESSOR", "Compressor"),
        ("CONVEYOR", "Conveyor"),
        ("BOILER", "Boiler"),
    ]

    STATUS_TYPES = [
        ("RUNNING", "Running"),
        ("IDLE", "Idle"),
        ("MAINTENANCE", "Maintenance"),
        ("OFFLINE", "Offline"),
    ]


    CRITICALITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]


    facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        related_name="machines"
    )

    asset_tag = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    machine_type = models.CharField(max_length=20,choices=MACHINE_TYPES)
    status = models.CharField(max_length=20,choices=STATUS_TYPES,default="RUNNING")
    installed_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=80, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)

    department = models.CharField(max_length=80, blank=True)
    plant_location = models.CharField(max_length=120, blank=True)

    criticality = models.CharField(max_length=20,choices=CRITICALITY_CHOICES,default="MEDIUM")

    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)    

    def __str__(self):
        return self.asset_tag


# 3. SENSOR

class Sensor(models.Model):

    SENSOR_CHOICES = [
        ("TEMPERATURE", "Temperature"),
        ("VIBRATION", "Vibration"),
        ("PRESSURE", "Pressure"),
    ]

    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT,
        related_name="sensors"
    )

    code = models.CharField(max_length=40, unique=True)
    sensor_type = models.CharField(
        max_length=20,
        choices=SENSOR_CHOICES
    )
    unit = models.CharField(max_length=10)

    min_threshold = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    max_threshold = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=80, blank=True)
    sensor_location = models.CharField(max_length=120, blank=True)

    installed_on = models.DateField(null=True, blank=True)
    last_calibrated = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            # At least one threshold must exist
            models.CheckConstraint(
                condition=(
                    Q(min_threshold__isnull=False) |
                    Q(max_threshold__isnull=False)
                ),
                name="sensor_requires_threshold"
            ),

            # If both limits exist, min must be less than max
            models.CheckConstraint(
                condition=(
                    Q(min_threshold__isnull=True) |
                    Q(max_threshold__isnull=True) |
                    Q(min_threshold__lt=F("max_threshold"))
                ),
                name="valid_sensor_threshold"
            ),
        ]

    def __str__(self):
        return self.code


# 4. READING


class Reading(models.Model):

    sensor = models.ForeignKey(Sensor,on_delete=models.PROTECT,related_name="readings")
    value = models.DecimalField(max_digits=10,decimal_places=2)
    recorded_at = models.DateTimeField(default=timezone.now)
    received_at = models.DateTimeField(auto_now_add=True)
    is_breach = models.BooleanField(default=False)

    def isbreach(self):

        min_value = self.sensor.min_threshold
        max_value = self.sensor.max_threshold

        return (
            (min_value is not None and self.value < min_value)
            or
            (max_value is not None and self.value > max_value)
        )

    def save(self, *args, **kwargs):

        self.is_breach = self.isbreach()

        super().save(*args, **kwargs)    

    class Meta:
        indexes = [
            models.Index(
                fields=["sensor", "-recorded_at"],
                name="idx_sensor_reading_time"
            )
        ]

    def __str__(self):
        return f"{self.sensor.code} - {self.value}"



# 5. ALERT


class Alert(models.Model):

    ALERT_CHOICES = [
        ("HIGH", "High"),
        ("LOW", "Low"),
    ]

    SEVERITY_CHOICES = [
        ("WARNING", "Warning"),
        ("CRITICAL", "Critical"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("ACKNOWLEDGED", "Acknowledged"),
        ("RESOLVED", "Resolved"),
    ]

    sensor = models.ForeignKey(Sensor,on_delete=models.CASCADE,related_name="alerts")
    reading = models.ForeignKey(Reading,on_delete=models.SET_NULL,null=True,blank=True,related_name="alerts")
    alert_type = models.CharField(max_length=20,choices=ALERT_CHOICES,default="LOW")
    severity = models.CharField(max_length=20,choices=SEVERITY_CHOICES,default="WARNING")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="OPEN")
    reading_value = models.DecimalField(max_digits=10,decimal_places=2)
    threshold_value = models.DecimalField(max_digits=10,decimal_places=2)
    occurrence_count = models.PositiveIntegerField(default=1)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    acknowledged_at = models.DateTimeField(null=True,blank=True)
    acknowledged_by = models.CharField(max_length=50,blank=True)
    resolved_at = models.DateTimeField(null=True,blank=True)
    resolution_note = models.TextField(blank=True)



    def set_alert_severity(self):

        if self.occurrence_count > 4:
            return "CRITICAL"

        return "WARNING"

    def save(self, *args, **kwargs):

        self.severity = self.set_alert_severity()

        if self.reading_value < self.threshold_value:
            self.alert_type = "LOW"
        else:
            self.alert_type = "HIGH"

        if self.status == "RESOLVED":
            self.resolved_at = timezone.now()

        if (
            self.status in ("ACKNOWLEDGED", "RESOLVED")
        ):
            self.acknowledged_at = timezone.now()

        super().save(*args, **kwargs)

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["sensor"],
                condition=Q(status="OPEN"),
                name="unique_open_sensor_alert"
            )
        ]

        indexes = [
            models.Index(
                fields=["status", "-created_at"],
                name="idx_alert_status_time"
            )
        ]

    def __str__(self):
        return f"{self.sensor.code} - {self.status}"

