"""
PLANTPULSE - DJANGO AUTOMATED TESTS

1. Reading model - threshold and breach detection
2. MachineUpdateForm - maintenance date validation
3. AlertUpdateForm - permitted editable fields
4. AlertsUpdateViews - alert status transitions

ARRANGE -> Prepare the data
ACT     -> Perform the operation
ASSERT  -> Verify the expected result
"""


from decimal import Decimal
from django.test import TestCase, SimpleTestCase
from django.contrib.auth import get_user_model
from .models import Facility, Machine, Sensor, Reading, Alert
from .forms import MachineUpdateForm, AlertUpdateForm


"""
1. READING MODEL TESTS

Purpose:
Verify that Reading.save() correctly determines whether
a sensor reading breaches its minimum or maximum threshold.

Our Reading model calculates is_breach automatically
when Reading.objects.create() calls save().

Test sensor thresholds:
Minimum = 10.00
Maximum = 80.00

45.00 -> Normal
90.00 -> High breach
5.00  -> Low breach
80.00 -> Normal (boundary value)
"""

class ReadingModelTests(TestCase):

    """
    setUp() runs BEFORE EACH test method.

    We prepare the same Facility, Machine and Sensor
    for every test.

    Each test gets isolated database state.
    """
    def setUp(self):

        """ARRANGE: Create a sample facility."""
        self.facility = Facility.objects.create(
            name="Test Plant",
            code="TEST-01"
        )

        """
        Create a machine belonging to the facility.

        facility=self.facility establishes
        the ForeignKey relationship.
        """
        self.machine = Machine.objects.create(
            facility=self.facility,
            asset_tag="TEST-M001",
            name="Test Motor",
            machine_type="MOTOR"
        )

        """
        Create a sensor belonging to the machine.

        We define minimum and maximum thresholds
        so that we can test breach detection.
        """
        self.sensor = Sensor.objects.create(
            machine=self.machine,
            code="TEST-TEMP-001",
            sensor_type="TEMPERATURE",
            unit="C",
            min_threshold=Decimal("10.00"),
            max_threshold=Decimal("80.00")
        )

    """
    TEST 1 - NORMAL SENSOR READING

    Reading = 45

    Since 10 <= 45 <= 80, this is not a breach.

    Expected: is_breach = False
    """
    def test_normal_reading(self):

        """
        ACT: Create a reading.

        objects.create() calls the model's save() method,
        which automatically calculates is_breach.
        """
        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("45.00")
        )

        """
        ASSERT:
        Check that Django marked the reading as normal.

        assertFalse() passes when the condition is False.
        """
        self.assertFalse(reading.is_breach)

    """
    TEST 2 - ABOVE MAXIMUM THRESHOLD

    Reading = 90
    Maximum = 80

    Since 90 > 80, this is a breach.

    Expected: is_breach = True
    """
    def test_high_temperature_breach(self):

        """ACT: Insert a reading above the maximum."""
        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("90.00")
        )

        """
        ASSERT:
        assertTrue() passes when the condition is True.
        """
        self.assertTrue(reading.is_breach)

    """
    TEST 3 - BELOW MINIMUM THRESHOLD

    Reading = 5
    Minimum = 10

    Since 5 < 10, this is a breach.

    Expected: is_breach = True
    """
    def test_low_temperature_breach(self):

        """ACT: Insert a reading below the minimum."""
        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("5.00")
        )

        """
        ASSERT:
        Verify that the lower-threshold check works.
        """
        self.assertTrue(reading.is_breach)

    """
    TEST 4 - READING EXACTLY AT MAXIMUM THRESHOLD

    Reading = 80
    Maximum = 80

    Our model checks value > max_threshold,
    not value >= max_threshold.

    Therefore, equality is allowed.

    Expected: is_breach = False
    """
    def test_reading_at_max_threshold(self):

        """ACT: Create reading equal to maximum threshold."""
        reading = Reading.objects.create(
            sensor=self.sensor,
            value=Decimal("80.00")
        )

        """
        ASSERT:
        The maximum boundary should not trigger a breach.
        """
        self.assertFalse(reading.is_breach)


"""
2. MACHINE FORM TESTS

Purpose:
Verify the validation logic in MachineUpdateForm.

The form contains:
- last_maintenance
- next_maintenance
- remarks

Validation rule:

next_maintenance must not be before last_maintenance.

We use SimpleTestCase because we are checking
form validation without saving database records.
"""

class MachineFormTests(SimpleTestCase):

    """
    TEST 1 - VALID MAINTENANCE DATES

    Last maintenance: 10 November
    Next maintenance: 20 November

    Next date is later than last date.

    Expected: form.is_valid() = True
    """
    def test_valid_maintenance_dates(self):

        """
        ARRANGE:
        Simulate the data submitted by an employee
        through the machine-editing HTML form.
        """
        form = MachineUpdateForm(data={
            "last_maintenance": "2026-11-10",
            "next_maintenance": "2026-11-20",
            "remarks": "Machine inspected"
        })

        """
        ACT + ASSERT:

        is_valid() executes Django field validation
        and our custom clean() method.

        assertTrue() verifies that the form is accepted.
        """
        self.assertTrue(form.is_valid())

    """
    TEST 2 - INVALID MAINTENANCE DATES

    Last maintenance: 20 November
    Next maintenance: 10 November

    Next maintenance occurs BEFORE last maintenance.

    Expected:
    form.is_valid() = False
    form.errors contains "next_maintenance"
    """
    def test_invalid_maintenance_dates(self):

        """
        ARRANGE:
        Supply invalid maintenance dates.
        """
        form = MachineUpdateForm(data={
            "last_maintenance": "2026-11-20",
            "next_maintenance": "2026-11-10",
            "remarks": "Machine inspected"
        })

        """
        ASSERT 1:
        Form validation must fail.
        """
        self.assertFalse(form.is_valid())

        """
        ASSERT 2:

        Check that the validation error is associated
        with the correct form field.

        form.errors is a dictionary-like object:

        {
          "next_maintenance": [
              "Next maintenance cannot be before..."
          ]
        }

        assertIn() checks whether a key/item exists.
        """
        self.assertIn(
            "next_maintenance",
            form.errors
        )

    """
    TEST 3 - SAME MAINTENANCE DATES

    Last maintenance: 20 November
    Next maintenance: 20 November

    Our form checks next_date < last_date.

    Since both dates are equal,
    this condition evaluates to False.

    Expected: form.is_valid() = True
    """
    def test_same_maintenance_dates(self):

        """
        ARRANGE:
        Both dates are identical.
        """
        form = MachineUpdateForm(data={
            "last_maintenance": "2026-11-20",
            "next_maintenance": "2026-11-20",
            "remarks": "Same day maintenance"
        })

        """
        ASSERT:
        Equality is allowed by our validation logic.
        """
        self.assertTrue(form.is_valid())


"""
3. ALERT FORM TESTS

Purpose:
Prevent employees from modifying backend-managed fields.

Only the following fields should be editable:

- status
- message
- resolution_note

Fields such as acknowledged_by, acknowledged_at
and resolved_at must be controlled by the backend.

This is also a regression test.

A regression test prevents a previously fixed bug
from accidentally being reintroduced.
"""

class AlertFormTests(SimpleTestCase):

    """TEST 1 - ALLOWED ALERT FORM FIELDS"""
    def test_only_allowed_fields(self):

        """
        ARRANGE:
        Create an empty form instance.

        No database record is required here.
        """
        form = AlertUpdateForm()

        """
        form.fields.keys() returns all fields
        that the ModelForm allows employees to submit.

        Example:
        dict_keys([
          "status",
          "message",
          "resolution_note"
        ])

        set() converts the collection into a set,
        allowing comparison regardless of field order.
        """

        """
        ASSERT:
        Verify the form contains exactly these fields.

        assertEqual(expected, actual) compares values.
        """
        self.assertEqual(
            set(form.fields.keys()),
            {
                "status",
                "message",
                "resolution_note"
            }
        )


"""
4. ALERT UPDATE VIEW TESTS

Purpose:
Test the actual AlertsUpdateViews Django CBV.

Unlike form tests, these tests simulate HTTP requests.

They verify:

- Employee authentication
- Form submission using POST
- Alert status changes
- Employee acknowledgement details
- Resolution notes
- Database persistence
- Validation errors

TestCase is required because we create database records.
"""

class AlertViewTests(TestCase):

    """
    COMMON TEST DATA

    setUp() runs before every test.

    It creates a logged-in employee
    and a complete alert relationship:

    Facility -> Machine -> Sensor -> Alert
    """
    def setUp(self):

        """
        Get the configured Django User model.

        This is preferred over importing User directly
        because projects may use custom User models.
        """
        User = get_user_model()

        """
        ARRANGE:
        Create a sample employee.
        """
        self.user = User.objects.create_user(
            username="emp001",
            password="test12345",
            first_name="Rahul",
            last_name="Sharma"
        )

        """
        Authenticate the employee in the test client.

        force_login() simulates an authenticated session.

        It does not require submitting a login form.

        This is necessary because our view uses
        LoginRequiredMixin.
        """
        self.client.force_login(self.user)

        """Create facility."""
        self.facility = Facility.objects.create(
            name="Test Plant",
            code="TEST-PLANT"
        )

        """Create machine associated with facility."""
        self.machine = Machine.objects.create(
            facility=self.facility,
            asset_tag="TEST-M001",
            name="Test Motor",
            machine_type="MOTOR"
        )

        """Create sensor associated with machine."""
        self.sensor = Sensor.objects.create(
            machine=self.machine,
            code="TEST-TEMP",
            sensor_type="TEMPERATURE",
            unit="C",
            max_threshold=Decimal("80.00")
        )

        """
        Create an OPEN alert.

        The reading value exceeds the threshold.
        """
        self.alert = Alert.objects.create(
            sensor=self.sensor,
            status="OPEN",
            reading_value=Decimal("90.00"),
            threshold_value=Decimal("80.00"),
            message="Temperature exceeded limit"
        )

        """
        Construct the URL for editing this alert.

        Example:
        /alerts/1/edit/

        The ID is dynamically generated by the database.
        """
        self.url = f"/alerts/{self.alert.id}/edit/"


    """
    TEST 1 - OPEN TO ACKNOWLEDGED

    Employee Rahul Sharma acknowledges an OPEN alert.

    Expected:

    - HTTP 302 redirect
    - Status becomes ACKNOWLEDGED
    - acknowledged_by contains employee's full name
    - acknowledged_at is populated
    """
    def test_open_to_acknowledged(self):

        """
        ACT:

        Simulate the employee submitting the alert form.

        self.client.post() sends an HTTP POST request
        directly to the Django view.
        """
        response = self.client.post(
            self.url,
            data={
                "status": "ACKNOWLEDGED",
                "message": "Investigating temperature",
                "resolution_note": ""
            }
        )

        """
        ASSERT 1:

        A successful UpdateView redirects
        to its success_url.

        HTTP 302 = Redirect.
        """
        self.assertEqual(response.status_code, 302)

        """
        Reload the alert from the test database.

        The POST request may have modified the row,
        but self.alert still contains older in-memory data.
        """
        self.alert.refresh_from_db()

        """
        ASSERT 2:
        Confirm the status was updated in PostgreSQL.
        """
        self.assertEqual(
            self.alert.status,
            "ACKNOWLEDGED"
        )

        """
        ASSERT 3:

        Our view uses:
        request.user.get_full_name()

        The employee's full name should be saved.
        """
        self.assertEqual(
            self.alert.acknowledged_by,
            "Rahul Sharma"
        )

        """
        ASSERT 4:

        Verify that the acknowledgement timestamp exists.

        assertIsNotNone() checks that the value is not None.
        """
        self.assertIsNotNone(
            self.alert.acknowledged_at
        )


    """
    TEST 2 - ACKNOWLEDGED TO RESOLVED

    An alert was already acknowledged by another employee.

    Rahul now resolves it.

    Expected:

    - HTTP 302 redirect
    - Status becomes RESOLVED
    - Resolution note is stored
    - Original acknowledged_by name is preserved
    - resolved_at timestamp is populated
    """
    def test_acknowledged_to_resolved(self):

        """
        ARRANGE:

        Change our sample alert from OPEN to ACKNOWLEDGED.

        Simulate an earlier acknowledgement
        by a different employee.
        """
        self.alert.status = "ACKNOWLEDGED"
        self.alert.acknowledged_by = "Original Employee"

        """
        Save those changes in the test database.

        This calls Alert.save(),
        which handles the acknowledgement timestamp.
        """
        self.alert.save()

        """
        ACT:

        Submit a new status and resolution note
        through the alert editing view.
        """
        response = self.client.post(
            self.url,
            data={
                "status": "RESOLVED",
                "message": "Temperature normalized",
                "resolution_note": "Cooling system repaired"
            }
        )

        """
        ASSERT 1:

        Successful update should redirect.
        """
        self.assertEqual(response.status_code, 302)

        """Reload the alert from the database."""
        self.alert.refresh_from_db()

        """
        ASSERT 2:

        Verify new status.
        """
        self.assertEqual(
            self.alert.status,
            "RESOLVED"
        )

        """
        ASSERT 3:

        Verify that the employee's resolution note
        was saved correctly.
        """
        self.assertEqual(
            self.alert.resolution_note,
            "Cooling system repaired"
        )

        """
        ASSERT 4:

        Verify that resolving the alert did not
        erase the employee who acknowledged it.

        This protects against the previous ModelForm bug.
        """
        self.assertEqual(
            self.alert.acknowledged_by,
            "Original Employee"
        )

        """
        ASSERT 5:

        Verify that a resolution timestamp was recorded.
        """
        self.assertIsNotNone(
            self.alert.resolved_at
        )


    """
    TEST 3 - RESOLUTION WITHOUT NOTE

    Employee attempts to resolve an alert
    without providing a resolution note.

    Business rule:
    A resolution note is mandatory.

    Expected:

    - HTTP 200 (edit form displayed again)
    - Error message is visible
    - Alert status remains OPEN
    """
    def test_resolution_without_note(self):

        """
        ACT:

        Submit RESOLVED with an empty resolution note.
        """
        response = self.client.post(
            self.url,
            data={
                "status": "RESOLVED",
                "message": "Temperature normalized",
                "resolution_note": ""
            }
        )

        """
        ASSERT 1:

        Invalid HTML forms are normally rendered again
        with HTTP 200.

        There should be no successful redirect.
        """
        self.assertEqual(response.status_code, 200)

        """
        ASSERT 2:

        Verify the HTML response contains
        the validation error from form_valid().

        assertContains() searches the HTTP response
        for the specified text.
        """
        self.assertContains(
            response,
            "Resolution note is required."
        )

        """Reload the database record."""
        self.alert.refresh_from_db()

        """
        ASSERT 3:

        Since form validation failed,
        the database should not change the alert status.
        """
        self.assertEqual(
            self.alert.status,
            "OPEN"
        )