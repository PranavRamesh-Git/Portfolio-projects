"""
PLANTPULSE - DJANGO AUTOMATED TESTS

1. Reading model - threshold and breach detection
2. MachineUpdateForm - maintenance date validation
3. AlertUpdateForm - permitted editable fields
4. AlertsUpdateViews - alert status transitions

"""


from decimal import Decimal
from django.test import TestCase, SimpleTestCase
from django.contrib.auth import get_user_model
from .models import Facility, Machine, Sensor, Reading, Alert
from .forms import MachineUpdateForm, AlertUpdateForm
from datetime import timedelta
from django.utils import timezone


"""

Test sensor thresholds:
Minimum = 10.00
Maximum = 80.00

45.00 -> Normal
90.00 -> High breach
5.00  -> Low breach
80.00 -> Normal (boundary value)
"""

class ReadingModelTests(TestCase):

    def setUp(self):

        self.facility = Facility.objects.create(name="Test Plant",code="TEST-01")

        self.machine = Machine.objects.create(
            facility=self.facility,
            asset_tag="TEST-M001",
            name="Test Motor",
            machine_type="MOTOR"
        )


        self.sensor = Sensor.objects.create(
            machine=self.machine,
            code="TEST-TEMP-001",
            sensor_type="TEMPERATURE",
            unit="C",
            min_threshold=Decimal("10.00"),
            max_threshold=Decimal("80.00")
        )


    def test_normal_reading(self):

        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("45.00")
        )

        self.assertFalse(reading.is_breach)


    def test_high_temperature_breach(self):


        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("90.00")
        )


        self.assertTrue(reading.is_breach)


    def test_low_temperature_breach(self):


        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("5.00")
        )

        self.assertTrue(reading.is_breach)

    def test_reading_at_max_threshold(self):

        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("80.00")
        )

        self.assertFalse(reading.is_breach)



class MachineFormTests(SimpleTestCase):

    def test_valid_maintenance_dates(self):
        form = MachineUpdateForm(data={
            "last_maintenance": "2026-11-10",
            "next_maintenance": "2026-11-20",
            "remarks": "Machine inspected"
        })

        self.assertTrue(form.is_valid())

 
    def test_invalid_maintenance_dates(self):
        form = MachineUpdateForm(data={
            "last_maintenance": "2026-11-20",
            "next_maintenance": "2026-11-10",
            "remarks": "Machine inspected"
        })


        self.assertFalse(form.is_valid())

        self.assertIn(
            "next_maintenance",
            form.errors
        )


    def test_same_maintenance_dates(self):

        form = MachineUpdateForm(data={
            "last_maintenance": "2026-11-20",
            "next_maintenance": "2026-11-20",
            "remarks": "Same day maintenance"
        })

        self.assertTrue(form.is_valid())




class AlertFormTests(SimpleTestCase):

    def test_only_allowed_fields(self):


        form = AlertUpdateForm()

        self.assertEqual(
            set(form.fields.keys()),
            {
                "status",
                "message",
                "resolution_note"
            }
        )



class AlertViewTests(TestCase):

    def setUp(self):

        User = get_user_model()
        self.user = User.objects.create_user(
            username="emp001",
            password="test12345",
            first_name="Rahul",
            last_name="Sharma"
        )

        self.client.force_login(self.user)

        self.facility = Facility.objects.create(
            name="Test Plant",
            code="TEST-PLANT"
        )

        self.machine = Machine.objects.create(
            facility=self.facility,
            asset_tag="TEST-M001",
            name="Test Motor",
            machine_type="MOTOR"
        )

        self.sensor = Sensor.objects.create(
            machine=self.machine,
            code="TEST-TEMP",
            sensor_type="TEMPERATURE",
            unit="C",
            max_threshold=Decimal("80.00")
        )


        self.alert = Alert.objects.create(
            sensor=self.sensor,
            status="OPEN",
            reading_value=Decimal("90.00"),
            threshold_value=Decimal("80.00"),
            message="Temperature exceeded limit"
        )

        self.url = f"/alerts/{self.alert.id}/edit/"


    def test_open_to_acknowledged(self):

        response = self.client.post(
            self.url,
            data={
                "status": "ACKNOWLEDGED",
                "message": "Investigating temperature",
                "resolution_note": ""
            }
        )

        self.assertEqual(response.status_code, 302)

        self.alert.refresh_from_db()


        self.assertEqual(
            self.alert.status,
            "ACKNOWLEDGED"
        )


        self.assertEqual(
            self.alert.acknowledged_by,
            "Rahul Sharma"
        )

        self.assertIsNotNone(
            self.alert.acknowledged_at
        )


    def test_acknowledged_to_resolved(self):

        self.alert.status = "ACKNOWLEDGED"
        self.alert.acknowledged_by = "Original Employee"

        self.alert.save()
        response = self.client.post(
            self.url,
            data={
                "status": "RESOLVED",
                "message": "Temperature normalized",
                "resolution_note": "Cooling system repaired"
            }
        )


        self.assertEqual(response.status_code, 302)


        self.alert.refresh_from_db()

        self.assertEqual(
            self.alert.status,
            "RESOLVED"
        )


        self.assertEqual(
            self.alert.resolution_note,
            "Cooling system repaired"
        )


        self.assertEqual(
            self.alert.acknowledged_by,
            "Original Employee"
        )


        self.assertIsNotNone(
            self.alert.resolved_at
        )


    def test_resolution_without_note(self):

        response = self.client.post(
            self.url,
            data={
                "status": "RESOLVED",
                "message": "Temperature normalized",
                "resolution_note": ""
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response,"Resolution note is required.")

        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status,"OPEN")

    def test_resolve_keeps_acknowledged_time(self):
        earlier = timezone.now() - timedelta(hours=2)
        # .update() writes straight to the DB, skipping Alert.save()
        Alert.objects.filter(pk=self.alert.pk).update(
            status="ACKNOWLEDGED", acknowledged_by="Original Employee", acknowledged_at=earlier
        )
        self.client.post(self.url, data={
            "status": "RESOLVED", "message": "Temperature normalized",
            "resolution_note": "Cooling system repaired"
        })
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.acknowledged_at, earlier)

    def test_changing_note_refreshes_resolved_time(self):
        earlier = timezone.now() - timedelta(hours=2)
        Alert.objects.filter(pk=self.alert.pk).update(
            status="RESOLVED", resolved_at=earlier, resolution_note="Cooling system repaired"
        )
        self.client.post(self.url, data={
            "status": "RESOLVED", "message": "Temperature exceeded limit",
            "resolution_note": "Cooling fan replaced"
        })
        self.alert.refresh_from_db()
        self.assertGreater(self.alert.resolved_at, earlier)

    def test_changing_only_message_keeps_resolved_time(self):
        earlier = timezone.now() - timedelta(hours=2)
        Alert.objects.filter(pk=self.alert.pk).update(
            status="RESOLVED", resolved_at=earlier, resolution_note="Cooling system repaired"
        )
        self.client.post(self.url, data={
            "status": "RESOLVED", "message": "Updated message only",
            "resolution_note": "Cooling system repaired"
        })
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.resolved_at, earlier)

    def test_open_to_resolved_records_no_acknowledgement(self):
        self.client.post(self.url, data={
            "status": "RESOLVED", "message": "Temperature exceeded limit",
            "resolution_note": "False alarm"
        })
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, "RESOLVED")
        self.assertEqual(self.alert.acknowledged_by, "")
        self.assertIsNone(self.alert.acknowledged_at)
