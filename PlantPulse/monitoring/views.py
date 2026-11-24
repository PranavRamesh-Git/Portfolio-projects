from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST,require_http_methods
import json
from .models import Facility, Machine, Sensor, Reading, Alert
from django.db.models import Q,F,Count,Sum,Max,Min,Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import MachineUpdateForm,AlertUpdateForm

@login_required
def home(request):
    facilities = Facility.objects.values()

    context = {
        "facilities" : facilities
    }

    return render(request, "monitoring/home.html",context)



@login_required
@require_POST
def get_dashboard(request):
    try:
        data = json.loads(request.body)
        facility_id = int(data.get("facility_id"))

        if facility_id <= 0:
            raise ValueError

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({
            "error": "Invalid facility ID or JSON body"
        }, status=400)

    sensors = (Sensor.objects.filter(machine__facility_id=facility_id).values("sensor_type").annotate(total=Count("code", distinct=True)).order_by("sensor_type"))

    machines = Machine.objects.filter(facility_id=facility_id).values().order_by("asset_tag")

    return JsonResponse({
        "sensors": list(sensors),
        "machines": list(machines),
        "sensor_count": Sensor.objects.filter( machine__facility_id=facility_id).count(),
        "machine_count": machines.count()
    })

@login_required
@require_POST
def get_sensor_readings(request):
    try:
        data = json.loads(request.body)
        facility_id = int(data.get("facility_id"))
        if facility_id <= 0:
            raise ValueError
    except(ValueError,TypeError,json.JSONDecodeError):
        return JsonResponse({
            "error": "Invalid facility ID or JSON body"
        },status=400)

    sensor_readings = []

    sensor_machines = (
        Sensor.objects
        .filter(machine__facility_id=facility_id)
        .values(
            "id",
            "code",
            "sensor_type",
            "unit",
            "min_threshold",
            "max_threshold",
            "machine_id",
            "machine__asset_tag",
            "machine__machine_type",
            "machine__status",
            "machine__name",
            "machine__criticality"
        )
    )

    for item in sensor_machines:

        sensor_id = item["id"]

        readings = (
            Reading.objects
            .filter(sensor_id=sensor_id)
            .values(
                "id",
                "value",
                "recorded_at",
                "received_at",
                "is_breach"
            )
            .order_by("-recorded_at", "-received_at")
        )

        item["readings"] = list(readings)

        sensor_readings.append(item)

    if len(sensor_readings) == 0:
        return JsonResponse({
            "status": "NIL"
        })
    else:
        return JsonResponse({
            "status": "success",
            "sensor_readings": sensor_readings
        })


@login_required
@require_POST
def get_sensor_alerts(request):

    try:
        data = json.loads(request.body)
        facility_id = int(data.get("facility_id"))

        if facility_id <= 0:
            raise ValueError

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({
            "error": "Invalid facility ID or JSON body"
        }, status=400)

    alerts = (
        Alert.objects
        .filter(sensor__machine__facility_id=facility_id)
        .values(
            "id",
            # Machine information
            "sensor__machine_id",
            "sensor__machine__asset_tag",
            "sensor__machine__machine_type",
            "sensor__machine__status",
            "sensor__machine__name",
            "sensor__machine__criticality",
            # Sensor information
            "sensor__code",
            "sensor__sensor_type",
            "sensor__unit",
            "sensor__min_threshold",
            "sensor__max_threshold",

            # Alert information
            "alert_type",
            "severity",
            "status",
            "reading_value",
            "threshold_value",
            "occurrence_count",
            "message",
            "created_at",
            "acknowledged_at",
            "acknowledged_by",
            "resolved_at",
            "resolution_note",
            "sensor_id",
            "reading_id"
        )
        .order_by("-created_at")
    )

    sensor_alerts = list(alerts)

    if not sensor_alerts:
        return JsonResponse({
            "status": "NIL",
            "sensor_alerts": []
        })

    return JsonResponse({
        "status": "success",
        "sensor_alerts": sensor_alerts
    })


class MachineUpdateView(LoginRequiredMixin, UpdateView):

    model = Machine

    form_class = MachineUpdateForm

    template_name = "monitoring/machine_form.html"

    success_url = reverse_lazy("home_page")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Machine updated successfully."
        )

        return super().form_valid(form)



class AlertsUpdateViews(LoginRequiredMixin, UpdateView):

    model = Alert
    form_class = AlertUpdateForm
    template_name = "monitoring/alert_form.html"
    success_url = reverse_lazy("home_page")

    def form_valid(self, form):

        old_status = Alert.objects.values_list(
            "status", flat=True
        ).get(pk=self.object.pk)

        new_status = form.cleaned_data["status"]


        # Prevent reopening resolved alerts
        if old_status == "RESOLVED" and new_status != "RESOLVED":

            form.add_error(
                "status",
                "Resolved alerts cannot be reopened."
            )

            return self.form_invalid(form)

        # Acknowledged alerts can only be resolved
        if old_status == "ACKNOWLEDGED" and new_status != "RESOLVED":

            form.add_error(
                "status",
                "Acknowledged alerts can only be resolved."
            )

            return self.form_invalid(form)

        # Resolution note is mandatory
        if new_status == "RESOLVED":

            note = form.cleaned_data.get("resolution_note", "")

            if not note.strip():

                form.add_error(
                    "resolution_note",
                    "Resolution note is required."
                )

                return self.form_invalid(form)

        # Record employee name
        if old_status == "OPEN" and new_status == "ACKNOWLEDGED":

            form.instance.acknowledged_by = (
                self.request.user.get_full_name()
                or self.request.user.username
            )

        if old_status == "RESOLVED" and "resolution_note" in form.changed_data:
            form.instance.resolved_at = timezone.now()
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Alert updated successfully."
        )

        return response


